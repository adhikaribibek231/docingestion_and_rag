"""FastAPI app wiring: lifecycle hooks, health check, and routers."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.session import init_db
from app.api import chat as chat_router
from app.api import document as doc_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the DB on startup and log lifecycle events."""
    logger.info("starting up")
    init_db()
    yield
    logger.info("shutting down")

app = FastAPI(
    title = settings.app_name,
    lifespan=lifespan
)
@app.get("/health")
async def health_check() -> dict:
    """Lightweight readiness probe."""
    return {"status": "ok"}

app.include_router(chat_router.router, prefix="/chat", tags=["chat"])
app.include_router(doc_router.router, prefix="/document", tags=["document"])
