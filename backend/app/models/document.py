"""Document metadata stored alongside vectors."""
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class Document(SQLModel, table = True):
    """Tracks uploaded document metadata and external ID used in vector store."""
    id: int | None = Field(default=None, primary_key=True)
    external_id: str = Field(index=True, unique=True)
    filename: str
    content_type: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
