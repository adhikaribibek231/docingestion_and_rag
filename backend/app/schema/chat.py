from pydantic import BaseModel

class ChatMessage(BaseModel):
    session_id: str
    message: str
    document_id: str | None= None

class ChatResponse(BaseModel):
    chat_answer: str
    session_id: str