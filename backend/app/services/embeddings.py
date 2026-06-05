import logging
from typing import List, Dict, Any, Optional
from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from app.config import settings

logger = logging.getLogger(__name__)

_embedding_model: Optional[SentenceTransformer] = None
_chroma_client = None
_collection = None

COLLECTION_NAME = "literature_chunks"


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedding_model


def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        if settings.CHROMADB_USE_HTTP:
            logger.info(f"Connecting to ChromaDB at {settings.CHROMADB_HOST}:{settings.CHROMADB_PORT}")
            _chroma_client = chromadb.HttpClient(
                host=settings.CHROMADB_HOST,
                port=settings.CHROMADB_PORT,
            )
        else:
            logger.info(f"Using persistent ChromaDB at {settings.CHROMADB_PERSIST_PATH}")
            _chroma_client = chromadb.PersistentClient(path=settings.CHROMADB_PERSIST_PATH)
    return _chroma_client


def get_collection():
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


def add_chunks(chunks_with_metadata: List[Dict[str, Any]]) -> None:
    """
    Add chunks to ChromaDB.
    Each item: { id: str, content: str, metadata: dict }
    """
    if not chunks_with_metadata:
        return

    collection = get_collection()
    ids = [c["id"] for c in chunks_with_metadata]
    texts = [c["content"] for c in chunks_with_metadata]
    metadatas = [c["metadata"] for c in chunks_with_metadata]

    embeddings = embed_texts(texts)

    # Upsert in batches
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.upsert(
            ids=ids[i:i + batch_size],
            embeddings=embeddings[i:i + batch_size],
            documents=texts[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size],
        )
    logger.info(f"Added {len(ids)} chunks to ChromaDB")


def search_similar(
    query: str,
    n_results: int = 8,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Search for similar chunks in ChromaDB.
    Returns list of { content, metadata, distance }.
    """
    collection = get_collection()
    query_embedding = embed_texts([query])[0]

    where = None
    if filters:
        conditions = []
        if filters.get("journal"):
            conditions.append({"journal": {"$eq": filters["journal"]}})
        if filters.get("date_from"):
            conditions.append({"pub_date": {"$gte": filters["date_from"]}})
        if filters.get("date_to"):
            conditions.append({"pub_date": {"$lte": filters["date_to"]}})
        if len(conditions) == 1:
            where = conditions[0]
        elif len(conditions) > 1:
            where = {"$and": conditions}

    kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": n_results,
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        kwargs["where"] = where

    try:
        results = collection.query(**kwargs)
    except Exception as e:
        logger.warning(f"ChromaDB query failed (possibly with filters): {e}")
        # Retry without filters
        kwargs.pop("where", None)
        results = collection.query(**kwargs)

    chunks = []
    if results and results.get("documents"):
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]
        for doc, meta, dist in zip(docs, metas, dists):
            chunks.append({"content": doc, "metadata": meta, "distance": dist})

    return chunks


def delete_chunks_by_article(pmid: str) -> None:
    """Delete all chunks for a given PMID."""
    collection = get_collection()
    try:
        collection.delete(where={"pmid": {"$eq": pmid}})
    except Exception as e:
        logger.warning(f"Failed to delete chunks for pmid {pmid}: {e}")
