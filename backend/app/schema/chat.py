from pydantic import BaseModel
from typing import List, Optional, Any


class RetrievedChunk(BaseModel):
    text: str
    document_id: Optional[str]
    chunk_id: Optional[int]
    score: float


class ChatMessage(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[RetrievedChunk]
