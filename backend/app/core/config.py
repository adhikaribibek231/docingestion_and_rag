"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Docinges RAG"
    database_url: str = "sqlite:///./PMrag.db"
    redis_url: str = "redis://localhost:6379/0"
    ollama_url: str = "http://localhost:11434"
settings = Settings()
