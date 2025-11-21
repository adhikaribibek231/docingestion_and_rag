"""Database session helpers and startup init."""
import logging
from sqlmodel import SQLModel, create_engine, Session

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    engine = create_engine(settings.database_url, echo=True)
except Exception as exc:
    engine = None
    logger.error("Failed to create database engine: %s", exc)


def init_db() -> None:
    """Create tables if the engine is available."""
    if engine is None:
        logger.warning("Database engine unavailable; skipping init.")
        return
    try:
        from app.models.document import Document  # noqa: F401
        from app.models.booking import Booking  # noqa: F401
        SQLModel.metadata.create_all(engine)
        logger.info("Database initialized")
    except Exception as exc:
        logger.error("Failed to initialize database: %s", exc)


def get_session():
    """Provide a SQLModel session dependency."""
    if engine is None:
        raise RuntimeError("Database engine is not initialized.")
    with Session(engine) as session:
        yield session
