from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schema.chat import ChatMessage, ChatResponse
from app.db.session import get_session
from app.services import rag_pipeline
from app.services.booking_intent import is_booking_request
from app.services.booking_pipeline import handle_booking

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    chat_request: ChatMessage,
    session: Session = Depends(get_session)
):

    if is_booking_request(chat_request.query):
        result = await handle_booking(
            user_id=chat_request.session_id,
            user_text=chat_request.query,
            db=session
        )
        return ChatResponse(booking=result)

    result = await rag_pipeline.answer_question(
        session_id=chat_request.session_id,
        question=chat_request.query,
        document_id=chat_request.document_id,
        db=session
    )

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"]
    )