from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    NCBI_API_KEY: str
    ANTHROPIC_API_KEY: str
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/litminer"
    CHROMADB_HOST: str = "localhost"
    CHROMADB_PORT: int = 8001
    CHROMADB_USE_HTTP: bool = True
    CHROMADB_PERSIST_PATH: str = "./chroma_data"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    MAX_RESULTS_PER_SEARCH: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
