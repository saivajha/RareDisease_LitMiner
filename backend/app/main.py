import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import search, query, articles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (for dev without alembic)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured.")
    except Exception as e:
        logger.warning(f"Could not create DB tables: {e}")

    # Initialize Qdrant collection
    try:
        from app.services.embeddings import get_qdrant_client
        get_qdrant_client()
        logger.info("Qdrant client initialized.")
    except Exception as e:
        logger.warning(f"Could not initialize Qdrant client: {e}")

    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="RareDisease LitMiner API",
    description="RAG-based scientific literature mining for rare disease research.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(articles.router, prefix="/api", tags=["articles"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
