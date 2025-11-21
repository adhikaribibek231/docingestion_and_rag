"""Booking table for storing scheduled meetings."""
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class Booking(SQLModel, table = True):
    """A confirmed booking tied to a chat session."""
    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    name: str
    email: str
    meeting_datetime: datetime 
    notes: str | None = None 
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
