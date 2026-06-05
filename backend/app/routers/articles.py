import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Article
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
