import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, Date, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pmid = Column(String, unique=True, nullable=False, index=True)
    pmcid = Column(String, nullable=True, index=True)
    doi = Column(String, nullable=True)
    title = Column(Text, nullable=False)
    abstract = Column(Text, nullable=True)
    authors = Column(JSON, default=list)
    journal = Column(String, nullable=True)
    pub_date = Column(Date, nullable=True)
    article_types = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    full_text_available = Column(Boolean, default=False)
    indexed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("Chunk", back_populates="article", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    chunk_type = Column(String(50), nullable=False)  # 'abstract' or 'fulltext'
    chroma_id = Column(String, nullable=True)

    article = relationship("Article", back_populates="chunks")


class SearchCache(Base):
    __tablename__ = "search_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String, unique=True, nullable=False, index=True)  # hash of keyword+filters
    keyword = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    pmids = Column(JSON, default=list)  # list of PMIDs returned by this search
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
