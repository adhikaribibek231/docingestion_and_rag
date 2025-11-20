from fastapi import FastAPI
from app.core.config import settings
from contextlib import asynccontextmanager
from app.db.session import init_db

@asynccontextmanager
async def lifespan(app):
    print("starting up")
    init_db()
    yield
    print("shutting down")

app = FastAPI(
    title = settings.app_name,
    lifespan=lifespan
)
@app.get("/health")
async def health_check():
    return {"status": "ok"}

from app.api import chat, document