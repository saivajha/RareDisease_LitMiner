import logging
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI

from app.database import get_db
from app.models import Article, Chunk
from app.schemas import SearchRequest, SearchResponse, ArticleOut
from app.services import pubmed as pubmed_service
from app.services import pmc as pmc_service
from app.services import embeddings as embed_service
from app.utils.chunking import chunk_abstract, chunk_fulltext
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/search", response_model=SearchResponse)
async def search_and_index(request: SearchRequest, db: Session = Depends(get_db)):
    """Search PubMed, fetch article metadata, chunk, embed, and store."""
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

    for art_data in articles_data:
        pmid = art_data["pmid"]

        # Upsert article in PostgreSQL
        db_article = db.query(Article).filter(Article.pmid == pmid).first()
        if db_article:
            # Update existing
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

        # Remove existing chunks for this article
        db.query(Chunk).filter(Chunk.article_id == db_article.id).delete()

        chunks_to_embed = []

        # Chunk abstract
        if art_data.get("abstract"):
            abstract_chunks = chunk_abstract(art_data["abstract"])
            for i, chunk_text in enumerate(abstract_chunks):
                chroma_id = f"{pmid}_abstract_{i}"
                db_chunk = Chunk(
                    article_id=db_article.id,
                    chunk_index=i,
                    content=chunk_text,
                    chunk_type="abstract",
                    chroma_id=chroma_id,
                )
                db.add(db_chunk)

                meta = {
                    "pmid": pmid,
                    "pmcid": art_data.get("pmcid") or "",
                    "doi": art_data.get("doi") or "",
                    "title": art_data.get("title") or "",
                    "authors": ", ".join(art_data.get("authors") or []),
                    "journal": art_data.get("journal") or "",
                    "pub_date": str(art_data.get("pub_date")) if art_data.get("pub_date") else "",
                    "chunk_type": "abstract",
                }
                chunks_to_embed.append({"id": chroma_id, "content": chunk_text, "metadata": meta})

        # Fetch and chunk PMC full text if requested
        if request.fetch_fulltext and art_data.get("pmcid"):
            try:
                fulltext = await pmc_service.fetch_pmc_fulltext(art_data["pmcid"])
                if fulltext:
                    ft_chunks = chunk_fulltext(fulltext)
                    for i, chunk_text in enumerate(ft_chunks):
                        chroma_id = f"{pmid}_fulltext_{i}"
                        db_chunk = Chunk(
                            article_id=db_article.id,
                            chunk_index=i,
                            content=chunk_text,
                            chunk_type="fulltext",
                            chroma_id=chroma_id,
                        )
                        db.add(db_chunk)

                        meta = {
                            "pmid": pmid,
                            "pmcid": art_data.get("pmcid") or "",
                            "doi": art_data.get("doi") or "",
                            "title": art_data.get("title") or "",
                            "authors": ", ".join(art_data.get("authors") or []),
                            "journal": art_data.get("journal") or "",
                            "pub_date": str(art_data.get("pub_date")) if art_data.get("pub_date") else "",
                            "chunk_type": "fulltext",
                        }
                        chunks_to_embed.append({"id": chroma_id, "content": chunk_text, "metadata": meta})

                    db_article.full_text_available = True
            except Exception as e:
                logger.warning(f"Failed to fetch full text for {art_data.get('pmcid')}: {e}")

        # Embed and store in ChromaDB
        if chunks_to_embed:
            try:
                embed_service.add_chunks(chunks_to_embed)
            except Exception as e:
                logger.warning(f"ChromaDB embed error for PMID {pmid}: {e}")

        indexed_articles.append(db_article)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"DB commit failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Refresh articles for response
    result_articles = []
    for a in indexed_articles:
        db.refresh(a)
        result_articles.append(ArticleOut.model_validate(a))

    # Generate a summary paragraph of the indexed articles
    summary = None
    if result_articles:
        try:
            summary = _generate_search_summary(request.keyword, result_articles)
        except Exception as e:
            logger.warning(f"Summary generation failed: {e}")

    return SearchResponse(indexed_count=len(result_articles), summary=summary, articles=result_articles)


def _generate_search_summary(keyword: str, articles: List[ArticleOut]) -> str:
    """Generate a concise summary paragraph of the indexed articles using OpenAI."""
    lines = []
    for i, a in enumerate(articles[:15]):  # cap at 15 to stay within token limits
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
        f"You have just retrieved {len(articles)} research articles from PubMed about: \"{keyword}\".\n\n"
        f"Write a concise 2–3 paragraph synthesis of what these articles collectively cover. "
        f"Write in flowing prose like a literature review introduction. "
        f"Use inline citations in the format [1], [2], etc. matching the reference numbers. "
        f"Highlight key themes, findings, or gaps across the articles.\n\n"
        f"Articles:\n{context}"
    )
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL_INGESTION,
        messages=[
            {"role": "system", "content": "You are a scientific literature analyst. Write concise, accurate synthesis paragraphs based only on the provided abstracts."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=600,
    )
    return response.choices[0].message.content
