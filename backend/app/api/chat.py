from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.schema.booking import BookingInfo
from app.schema.chat import ChatMessage, ChatResponse
from app.db.session import get_session
from app.services import rag_pipeline
from app.services.booking_pipeline import handle_booking

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    chat_message: ChatMessage,
    session: Session = Depends(get_session)
):
    result = await rag_pipeline.answer_question(
        session_id=chat_message.session_id,
        question=chat_message.message,
        db=session
    )

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"]
    )


@router.post("/book")
async def book_interview(
    booking_info: BookingInfo,
    session: Session = Depends(get_session)
):
    result = await handle_booking(
        user_id=booking_info.user_id,
        user_text=booking_info.notes,
        db=session
    )
    return result
