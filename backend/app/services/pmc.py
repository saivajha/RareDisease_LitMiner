import asyncio
import httpx
import logging
from typing import Optional
from lxml import etree

from app.config import settings

logger = logging.getLogger(__name__)

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


async def fetch_pmc_fulltext(pmcid: str) -> Optional[str]:
    """Fetch PMC Open Access full text via efetch and return concatenated body text."""
    # Normalize PMCID - remove 'PMC' prefix if present for the API call
    numeric_id = pmcid.replace("PMC", "").strip()

    params = {
        "db": "pmc",
        "id": numeric_id,
        "rettype": "full",
        "retmode": "xml",
        "api_key": settings.NCBI_API_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(f"{EUTILS_BASE}efetch.fcgi", params=params)
            resp.raise_for_status()
            xml_content = resp.content

        await asyncio.sleep(0.34)

        return _parse_pmc_xml(xml_content)
    except Exception as e:
        logger.warning(f"Failed to fetch PMC full text for {pmcid}: {e}")
        return None


def _parse_pmc_xml(xml_bytes: bytes) -> Optional[str]:
    """Parse PMC XML and extract body text sections."""
    try:
        root = etree.fromstring(xml_bytes)
    except Exception as e:
        logger.error(f"Failed to parse PMC XML: {e}")
        return None

    text_parts = []

    # Extract title
    for title in root.xpath("//article-title"):
        text = "".join(title.itertext()).strip()
        if text:
            text_parts.append(f"Title: {text}")

    # Extract abstract
    for abstract in root.xpath("//abstract"):
        text = "".join(abstract.itertext()).strip()
        if text:
            text_parts.append(f"Abstract: {text}")

    # Extract body sections
    for sec in root.xpath("//body//sec"):
        sec_title_nodes = sec.xpath("title")
        sec_title = "".join(sec_title_nodes[0].itertext()).strip() if sec_title_nodes else ""

        paragraphs = []
        for p in sec.xpath("p"):
            p_text = "".join(p.itertext()).strip()
            if p_text:
                paragraphs.append(p_text)

        if paragraphs:
            if sec_title:
                text_parts.append(f"\n{sec_title}\n" + " ".join(paragraphs))
            else:
                text_parts.append(" ".join(paragraphs))

    if not text_parts:
        # Fallback: extract all text
        all_text = "".join(root.itertext()).strip()
        return all_text if all_text else None

    return "\n\n".join(text_parts)
