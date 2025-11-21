from pydantic import BaseModel
from typing import List, Optional, Any


class RetrievedChunk(BaseModel):
    text: str
    document_id: Optional[str]
    chunk_id: Optional[int]
    score: float


class ChatMessage(BaseModel):
    session_id: str
    query: str
    document_id: str | None = None


class ChatResponse(BaseModel):
    answer: str | None = None
    sources: List[RetrievedChunk] | None = None
    booking: dict | None = None