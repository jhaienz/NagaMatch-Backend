from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "NagaMatch API"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/nagamatch"

    # File Upload
    upload_dir: str = "uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB

    # ChromaDB
    chroma_persist_dir: str = "data/chroma"

    # Matching
    match_threshold: float = 0.75
    max_matches: int = 10

    # Embedding model
    embedding_model: str = "all-MiniLM-L6-v2"

    # Optional API keys
    gemini: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
