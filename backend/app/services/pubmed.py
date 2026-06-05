import asyncio
import httpx
from typing import List, Optional, Dict, Any
from datetime import date
import logging
from lxml import etree

from app.config import settings

logger = logging.getLogger(__name__)

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


async def esearch(term: str, max_results: int = 20, date_from: Optional[str] = None,
                  date_to: Optional[str] = None) -> List[str]:
    """Search PubMed and return list of PMIDs."""
    params = {
        "db": "pubmed",
        "term": term,
        "retmax": max_results,
        "retmode": "json",
        "api_key": settings.NCBI_API_KEY,
    }
    if date_from:
        params["mindate"] = date_from
        params["datetype"] = "pdat"
    if date_to:
        params["maxdate"] = date_to
        params["datetype"] = "pdat"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{EUTILS_BASE}esearch.fcgi", params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("esearchresult", {}).get("idlist", [])


async def efetch_articles(pmids: List[str]) -> List[Dict[str, Any]]:
    """Fetch article details for a list of PMIDs."""
    if not pmids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "xml",
        "retmode": "xml",
        "api_key": settings.NCBI_API_KEY,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(f"{EUTILS_BASE}efetch.fcgi", params=params)
        resp.raise_for_status()
        xml_content = resp.content

    await asyncio.sleep(0.34)  # Rate limiting

    return _parse_pubmed_xml(xml_content)


def _get_text(element, xpath: str, default: str = "") -> str:
    try:
        nodes = element.xpath(xpath)
        if nodes:
            if hasattr(nodes[0], 'text') and nodes[0].text:
                return nodes[0].text.strip()
            elif isinstance(nodes[0], str):
                return nodes[0].strip()
    except Exception:
        pass
    return default


def _parse_pubmed_xml(xml_bytes: bytes) -> List[Dict[str, Any]]:
    articles = []
    try:
        root = etree.fromstring(xml_bytes)
    except Exception as e:
        logger.error(f"Failed to parse PubMed XML: {e}")
        return articles

    for article_elem in root.xpath("//PubmedArticle"):
        try:
            art = _parse_single_article(article_elem)
            if art:
                articles.append(art)
        except Exception as e:
            logger.warning(f"Error parsing article: {e}")

    return articles


def _parse_single_article(elem) -> Optional[Dict[str, Any]]:
    # PMID
    pmid_nodes = elem.xpath(".//PMID")
    pmid = pmid_nodes[0].text.strip() if pmid_nodes else None
    if not pmid:
        return None

    # Title
    title_parts = elem.xpath(".//ArticleTitle//text()")
    title = " ".join(title_parts).strip() or "No title"

    # Abstract
    abstract_parts = elem.xpath(".//AbstractText//text()")
    abstract = " ".join(abstract_parts).strip() or None

    # Authors
    authors = []
    for author in elem.xpath(".//Author"):
        last = _get_text(author, "LastName")
        first = _get_text(author, "ForeName")
        if last:
            authors.append(f"{last}, {first}".strip(", "))

    # Journal
    journal = _get_text(elem, ".//Journal/Title") or _get_text(elem, ".//ISOAbbreviation")

    # Publication date
    pub_date = None
    try:
        year = _get_text(elem, ".//PubDate/Year")
        month = _get_text(elem, ".//PubDate/Month") or "01"
        day = _get_text(elem, ".//PubDate/Day") or "01"
        if year:
            # Handle month names
            month_map = {
                "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
            }
            if month in month_map:
                month = month_map[month]
            pub_date = date(int(year), int(month), int(day))
    except Exception:
        pass

    # Article types
    article_types = [pt.text.strip() for pt in elem.xpath(".//PublicationTypeList/PublicationType") if pt.text]

    # Keywords
    keywords = [kw.text.strip() for kw in elem.xpath(".//KeywordList/Keyword") if kw.text]

    # IDs from PubmedData
    pmcid = None
    doi = None
    for article_id in elem.xpath(".//PubmedData/ArticleIdList/ArticleId"):
        id_type = article_id.get("IdType", "")
        id_val = article_id.text.strip() if article_id.text else ""
        if id_type == "pmc" and id_val:
            pmcid = id_val
        elif id_type == "doi" and id_val:
            doi = id_val

    return {
        "pmid": pmid,
        "pmcid": pmcid,
        "doi": doi,
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "journal": journal,
        "pub_date": pub_date,
        "article_types": article_types,
        "keywords": keywords,
    }


async def search_and_fetch(
    keyword: str,
    max_results: int = 20,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    journal_filter: Optional[str] = None,
    article_type_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Full pipeline: search then fetch article details."""
    pmids = await esearch(keyword, max_results=max_results, date_from=date_from, date_to=date_to)
    if not pmids:
        return []

    # Fetch in batches of 20
    all_articles = []
    batch_size = 20
    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i + batch_size]
        articles = await efetch_articles(batch)
        all_articles.extend(articles)
        if i + batch_size < len(pmids):
            await asyncio.sleep(0.34)

    # Post-filter by journal if requested
    if journal_filter:
        jf = journal_filter.lower()
        all_articles = [a for a in all_articles if a.get("journal") and jf in a["journal"].lower()]

    return all_articles
