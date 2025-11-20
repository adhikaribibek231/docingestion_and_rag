from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from app.schema.document import docingest, ChunkStrategy
from app.schema.chat import ChatMessage, ChatResponse

router = APIRouter()

@router.post("/message/", response_model = ChatResponse)
async def chat_message(
    chat_message: ChatMessage
):
    return 'dummy response'