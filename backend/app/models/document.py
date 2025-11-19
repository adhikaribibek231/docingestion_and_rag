from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class Document(SQLModel, table = True):
    id: int | None = Field(default=None, primary_key=True)
    external_id: str = Field(index=True, unique=True)
    filename: str
    content_type: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))