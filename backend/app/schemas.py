from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date, datetime
import uuid


class ArticleBase(BaseModel):
    pmid: str
    pmcid: Optional[str] = None
    doi: Optional[str] = None
    title: str
    abstract: Optional[str] = None
    authors: List[str] = []
    journal: Optional[str] = None
    pub_date: Optional[date] = None
    article_types: List[str] = []
    keywords: List[str] = []
    full_text_available: bool = False


class ArticleCreate(ArticleBase):
    pass


class ArticleOut(ArticleBase):
    id: uuid.UUID
    indexed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    keyword: str
    max_results: int = 20
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    journal_filter: Optional[str] = None
    fetch_fulltext: bool = False


class SearchResponse(BaseModel):
    indexed_count: int
    summary: Optional[str] = None
    articles: List[ArticleOut]


class QueryFilters(BaseModel):
    keyword: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    journal: Optional[str] = None


class QueryRequest(BaseModel):
    question: str
    filters: Optional[QueryFilters] = None


class SourceCitation(BaseModel):
    pmid: str
    pmcid: Optional[str] = None
    doi: Optional[str] = None
    title: str
    journal: Optional[str] = None
    pub_date: Optional[str] = None
    authors: List[str] = []


class QueryResponse(BaseModel):
    answer: str
    disclaimer: str
    sources: List[SourceCitation]


class ArticleListResponse(BaseModel):
    articles: List[ArticleOut]
    total: int
