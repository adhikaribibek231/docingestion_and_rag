from fastapi import FastAPI
from app.core.config import settings
from contextlib import asynccontextmanager
from app.db.session import init_db
from app.api import chat as chat_router
from app.api import document as doc_router

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

app.include_router(chat_router.router, prefix="/chat", tags=["chat"])
app.include_router(doc_router.router, prefix="/document", tags=["document"])