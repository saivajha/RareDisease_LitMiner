import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.database import get_db
from app.models import Article, Chunk, SearchCache
from app.schemas import ArticleListResponse, ArticleOut

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/articles", response_model=ArticleListResponse)
def list_articles(
    keyword: Optional[str] = Query(None),
    journal: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List indexed articles with optional filtering."""
    q = db.query(Article)

    if keyword:
        kw = f"%{keyword}%"
        q = q.filter(
            or_(
                Article.title.ilike(kw),
                Article.abstract.ilike(kw),
            )
        )

    if journal:
        q = q.filter(Article.journal.ilike(f"%{journal}%"))

    if date_from:
        q = q.filter(Article.pub_date >= date_from)

    if date_to:
        q = q.filter(Article.pub_date <= date_to)

    total = q.count()
    articles = q.order_by(Article.indexed_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return ArticleListResponse(
        articles=[ArticleOut.model_validate(a) for a in articles],
        total=total,
    )


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Return shared database statistics."""
    article_count = db.query(func.count(Article.id)).scalar()
    chunk_count = db.query(func.count(Chunk.id)).scalar()
    cached_searches = db.query(func.count(SearchCache.id)).scalar()
    journals = db.query(Article.journal).filter(Article.journal.isnot(None)).distinct().count()
    recent = db.query(SearchCache).order_by(SearchCache.updated_at.desc()).limit(5).all()

    return {
        "total_articles": article_count,
        "total_chunks_embedded": chunk_count,
        "cached_searches": cached_searches,
        "unique_journals": journals,
        "recent_searches": [
            {"keyword": s.keyword, "article_count": len(s.pmids or []), "updated_at": str(s.updated_at)}
            for s in recent
        ],
    }
