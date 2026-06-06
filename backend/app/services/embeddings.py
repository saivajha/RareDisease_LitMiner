import logging
import uuid
from typing import List, Dict, Any, Optional
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter,
    FieldCondition, MatchValue, Range
)
from app.config import settings

logger = logging.getLogger(__name__)

_openai_client: Optional[OpenAI] = None
_qdrant_client: Optional[QdrantClient] = None
VECTOR_SIZE = 1536  # text-embedding-3-small dimensions

def get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client

def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        # Ensure collection exists
        existing = [c.name for c in _qdrant_client.get_collections().collections]
        if settings.QDRANT_COLLECTION not in existing:
            _qdrant_client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info(f"Created Qdrant collection: {settings.QDRANT_COLLECTION}")
    return _qdrant_client

def embed_texts(texts: List[str]) -> List[List[float]]:
    client = get_openai_client()
    response = client.embeddings.create(
        input=texts,
        model=settings.OPENAI_EMBEDDING_MODEL,
    )
    return [item.embedding for item in response.data]

def add_chunks(chunks_with_metadata: List[Dict[str, Any]]) -> None:
    if not chunks_with_metadata:
        return
    client = get_qdrant_client()
    texts = [c["content"] for c in chunks_with_metadata]
    embeddings = embed_texts(texts)
    points = []
    for chunk, embedding in zip(chunks_with_metadata, embeddings):
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "chroma_id": chunk["id"],  # keep for compatibility
                **chunk["metadata"],
                "content": chunk["content"],
            }
        ))
    batch_size = 100
    for i in range(0, len(points), batch_size):
        client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=points[i:i+batch_size],
        )
    logger.info(f"Added {len(points)} chunks to Qdrant")

def search_similar(
    query: str,
    n_results: int = 8,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    client = get_qdrant_client()
    query_embedding = embed_texts([query])[0]

    qdrant_filter = None
    if filters:
        conditions = []
        if filters.get("journal"):
            conditions.append(FieldCondition(key="journal", match=MatchValue(value=filters["journal"])))
        if len(conditions) == 1:
            qdrant_filter = Filter(must=conditions)
        elif len(conditions) > 1:
            qdrant_filter = Filter(must=conditions)

    results = client.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=query_embedding,
        limit=n_results,
        query_filter=qdrant_filter,
        with_payload=True,
    )

    chunks = []
    for hit in results:
        payload = hit.payload or {}
        content = payload.pop("content", "")
        chunks.append({"content": content, "metadata": payload, "distance": 1 - hit.score})
    return chunks

def delete_chunks_by_article(pmid: str) -> None:
    client = get_qdrant_client()
    try:
        client.delete(
            collection_name=settings.QDRANT_COLLECTION,
            points_selector=Filter(must=[FieldCondition(key="pmid", match=MatchValue(value=pmid))]),
        )
    except Exception as e:
        logger.warning(f"Failed to delete chunks for pmid {pmid}: {e}")
