from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    NCBI_API_KEY: str
    OPENAI_API_KEY: str
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/litminer"
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "literature_chunks"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_MODEL_INGESTION: str = "gpt-4.1-mini"
    OPENAI_MODEL_ANSWER: str = "gpt-4.1-mini"
    MAX_RESULTS_PER_SEARCH: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
