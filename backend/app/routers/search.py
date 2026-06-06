import hashlib
import logging
import uuid
from datetime import datetime
from typing import List, Set

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI

from app.database import get_db
from app.models import Article, Chunk, SearchCache
from app.schemas import SearchRequest, SearchResponse, ArticleOut
from app.services import pubmed as pubmed_service
from app.services import pmc as pmc_service
from app.services import embeddings as embed_service
from app.utils.chunking import chunk_abstract, chunk_fulltext
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


def _cache_key(keyword: str, date_from: str, date_to: str, journal_filter: str) -> str:
    raw = f"{keyword.lower().strip()}|{date_from or ''}|{date_to or ''}|{journal_filter or ''}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _already_embedded(pmid: str, db: Session) -> bool:
    """Returns True if this article already has chunks in the DB (i.e. already embedded)."""
    article = db.query(Article).filter(Article.pmid == pmid).first()
    if not article:
        return False
    return db.query(Chunk).filter(Chunk.article_id == article.id).count() > 0


@router.post("/search", response_model=SearchResponse)
async def search_and_index(request: SearchRequest, db: Session = Depends(get_db)):
    """Search PubMed, skip already-indexed articles, embed only new ones, cache summaries."""
    cache_key = _cache_key(request.keyword, request.date_from, request.date_to, request.journal_filter)

    # Fetch PMIDs from PubMed (cheap — no embeddings yet)
    try:
        articles_data = await pubmed_service.search_and_fetch(
            keyword=request.keyword,
            max_results=request.max_results,
            date_from=request.date_from,
            date_to=request.date_to,
            journal_filter=request.journal_filter,
        )
    except Exception as e:
        logger.error(f"PubMed search failed: {e}")
        raise HTTPException(status_code=502, detail=f"PubMed search failed: {str(e)}")

    indexed_articles = []
    new_pmids: Set[str] = set()
    cached_count = 0

    for art_data in articles_data:
        pmid = art_data["pmid"]
        already_done = _already_embedded(pmid, db)

        # Always upsert metadata in PostgreSQL
        db_article = db.query(Article).filter(Article.pmid == pmid).first()
        if db_article:
            if not already_done:
                for key, val in art_data.items():
                    setattr(db_article, key, val)
                db_article.indexed_at = datetime.utcnow()
        else:
            db_article = Article(**art_data)
            db.add(db_article)

        try:
            db.flush()
        except Exception as e:
            db.rollback()
            logger.warning(f"DB flush error for PMID {pmid}: {e}")
            continue

        if already_done:
            # Article already embedded — skip Qdrant, reuse existing vectors
            cached_count += 1
            logger.info(f"PMID {pmid} already indexed — skipping re-embedding")
            indexed_articles.append(db_article)
            continue

        # New article — chunk and embed
        new_pmids.add(pmid)
        chunks_to_embed = []

        if art_data.get("abstract"):
            for i, chunk_text in enumerate(chunk_abstract(art_data["abstract"])):
                chroma_id = f"{pmid}_abstract_{i}"
                db.add(Chunk(article_id=db_article.id, chunk_index=i, content=chunk_text,
                             chunk_type="abstract", chroma_id=chroma_id))
                chunks_to_embed.append({"id": chroma_id, "content": chunk_text, "metadata": {
                    "pmid": pmid, "pmcid": art_data.get("pmcid") or "",
                    "doi": art_data.get("doi") or "", "title": art_data.get("title") or "",
                    "authors": ", ".join(art_data.get("authors") or []),
                    "journal": art_data.get("journal") or "",
                    "pub_date": str(art_data.get("pub_date")) if art_data.get("pub_date") else "",
                    "chunk_type": "abstract",
                }})

        if request.fetch_fulltext and art_data.get("pmcid"):
            try:
                fulltext = await pmc_service.fetch_pmc_fulltext(art_data["pmcid"])
                if fulltext:
                    for i, chunk_text in enumerate(chunk_fulltext(fulltext)):
                        chroma_id = f"{pmid}_fulltext_{i}"
                        db.add(Chunk(article_id=db_article.id, chunk_index=i, content=chunk_text,
                                     chunk_type="fulltext", chroma_id=chroma_id))
                        chunks_to_embed.append({"id": chroma_id, "content": chunk_text, "metadata": {
                            "pmid": pmid, "pmcid": art_data.get("pmcid") or "",
                            "doi": art_data.get("doi") or "", "title": art_data.get("title") or "",
                            "authors": ", ".join(art_data.get("authors") or []),
                            "journal": art_data.get("journal") or "",
                            "pub_date": str(art_data.get("pub_date")) if art_data.get("pub_date") else "",
                            "chunk_type": "fulltext",
                        }})
                    db_article.full_text_available = True
            except Exception as e:
                logger.warning(f"Full text fetch failed for {art_data.get('pmcid')}: {e}")

        if chunks_to_embed:
            try:
                embed_service.add_chunks(chunks_to_embed)
            except Exception as e:
                logger.warning(f"Qdrant embed error for PMID {pmid}: {e}")

        indexed_articles.append(db_article)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"DB commit failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    result_articles = []
    for a in indexed_articles:
        db.refresh(a)
        result_articles.append(ArticleOut.model_validate(a))

    new_count = len(new_pmids)

    # Check summary cache — only regenerate if there are new articles
    cached_entry = db.query(SearchCache).filter(SearchCache.cache_key == cache_key).first()
    summary = None

    if cached_entry and new_count == 0:
        # Fully cached — reuse summary, zero OpenAI calls
        summary = cached_entry.summary
        logger.info(f"Cache hit for '{request.keyword}' — reusing summary, 0 new articles")
    elif result_articles:
        # Generate new summary (new articles found, or first time)
        try:
            summary = _generate_search_summary(request.keyword, result_articles)
            # Upsert cache entry
            if cached_entry:
                cached_entry.summary = summary
                cached_entry.pmids = [a.pmid for a in result_articles]
                cached_entry.updated_at = datetime.utcnow()
            else:
                db.add(SearchCache(
                    cache_key=cache_key,
                    keyword=request.keyword,
                    summary=summary,
                    pmids=[a.pmid for a in result_articles],
                ))
            db.commit()
        except Exception as e:
            logger.warning(f"Summary generation failed: {e}")

    return SearchResponse(
        indexed_count=len(result_articles),
        new_count=new_count,
        cached_count=cached_count,
        summary=summary,
        articles=result_articles,
    )


def _generate_search_summary(keyword: str, articles: List[ArticleOut]) -> str:
    lines = []
    for i, a in enumerate(articles[:15]):
        authors = a.authors or []
        first_author = authors[0].split(",")[0] if authors else "Unknown"
        et_al = " et al." if len(authors) > 1 else ""
        year = str(a.pub_date)[:4] if a.pub_date else "n.d."
        abstract_snippet = (a.abstract or "")[:300].rstrip()
        lines.append(
            f"[{i+1}] {first_author}{et_al} ({year}). {a.title}. {a.journal or ''}.\n"
            f"Abstract: {abstract_snippet}..."
        )
    context = "\n\n".join(lines)
    prompt = (
        f"You have retrieved {len(articles)} PubMed articles about: \"{keyword}\".\n\n"
        f"Write a concise 2–3 paragraph synthesis in flowing prose like a literature review. "
        f"Use inline citations [1], [2], etc. Highlight key themes, findings, and gaps.\n\n"
        f"Articles:\n{context}"
    )
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL_INGESTION,
        messages=[
            {"role": "system", "content": "You are a scientific literature analyst. Synthesize concisely based only on the provided abstracts."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=600,
    )
    return response.choices[0].message.content
