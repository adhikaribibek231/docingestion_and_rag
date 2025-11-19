from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Palm Mind RAG"
    database_url: str = "sqlite:///./PM_rag.db"
settings = Settings()