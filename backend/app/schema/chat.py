"""Pydantic schemas for chat requests and responses."""
from pydantic import BaseModel
from typing import List, Optional, Any


class RetrievedChunk(BaseModel):
    """A chunk returned from vector search."""
    text: str
    document_id: Optional[str]
    chunk_id: Optional[int]
    score: float


class ChatMessage(BaseModel):
    """Inbound chat payload from the client."""
    session_id: str
    query: str
    document_id: str | None = None


class ChatResponse(BaseModel):
    """LLM answer plus optional source snippets and booking info."""
    answer: str | None = None
    sources: List[RetrievedChunk] | None = None
    booking: dict | None = None
