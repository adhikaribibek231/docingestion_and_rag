from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.schema.chat import ChatMessage, ChatResponse
from app.db.session import get_session
from app.services import rag_pipeline
from app.services.booking_intent import is_booking_request
from app.services.booking_pipeline import handle_booking, has_booking_draft

router = APIRouter()

@router.post("/message", response_model=ChatResponse, response_model_exclude_none=True)
async def chat_message(
    chat_request: ChatMessage,
    session: Session = Depends(get_session)
):

    if is_booking_request(chat_request.query) or has_booking_draft(chat_request.session_id):
        try:
            result = await handle_booking(
                user_id=chat_request.session_id,
                user_text=chat_request.query,
                db=session
            )
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Booking pipeline failed: {exc}")

        message = result.get("message")
        if not message and result.get("error") is False:
            dt_value = result.get("datetime")
            date_str = dt_value.strftime("%Y-%m-%d at %H:%M") if isinstance(dt_value, datetime) else str(dt_value)
            message = f"Booking confirmed for {date_str}."

        return ChatResponse(
            answer=message,
            sources=[],
            booking=result
        )

    try:
        result = await rag_pipeline.answer_question(
            session_id=chat_request.session_id,
            question=chat_request.query,
            document_id=chat_request.document_id,
            db=session
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Chat pipeline failed: {exc}")

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"]
    )
