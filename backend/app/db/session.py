from sqlmodel import Field, SQLModel, create_engine, Session

from app.core.config import settings

try:
    engine = create_engine(settings.database_url, echo=True)
except Exception as exc:
    engine = None
    print(f"Failed to create database engine: {exc}")


def init_db():
    if engine is None:
        print("Database engine unavailable; skipping init.")
        return
    try:
        from app.models.document import Document
        from app.models.booking import Booking
        SQLModel.metadata.create_all(engine)
    except Exception as exc:
        print(f"Failed to initialize database: {exc}")


def get_session():
    if engine is None:
        raise RuntimeError("Database engine is not initialized.")
    with Session(engine) as session:
        yield session
