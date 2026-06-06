import logging
from fastapi import APIRouter, HTTPException
from app.schemas import QueryRequest, QueryResponse
from app.services.rag import run_rag

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/query", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    """RAG Q&A over indexed literature."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    filters = None
    if request.filters:
        filters = {
            "journal": request.filters.journal,
            "date_from": request.filters.date_from,
            "date_to": request.filters.date_to,
        }

    try:
        result = run_rag(question=request.question, filters=filters)
    except Exception as e:
        logger.error(f"RAG pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    return QueryResponse(
        answer=result["answer"],
        disclaimer=result["disclaimer"],
        sources=result["sources"],
    )
