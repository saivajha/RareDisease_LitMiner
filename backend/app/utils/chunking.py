from typing import List


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks by word count."""
    if not text or not text.strip():
        return []

    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        if end >= len(words):
            break
        start += chunk_size - overlap

    return chunks


def chunk_abstract(abstract: str) -> List[str]:
    """Chunk an abstract - usually short enough for 1-2 chunks."""
    return chunk_text(abstract, chunk_size=300, overlap=30)


def chunk_fulltext(fulltext: str) -> List[str]:
    """Chunk full text with larger windows."""
    return chunk_text(fulltext, chunk_size=500, overlap=50)
