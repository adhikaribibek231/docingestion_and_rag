from datetime import datetime

from sqlmodel import Session

from app.models.booking import Booking
from app.services.booking_extractor import extract_booking_info
from app.services.date_normalizer import normalize_date_time


async def handle_booking(user_id: str, user_text: str, db: Session):
    extracted = await extract_booking_info(user_text)

    name = extracted.get("name")
    email = extracted.get("email")
    raw_date = extracted.get("date")
    raw_time = extracted.get("time")

    missing = []
    if not name:
        missing.append("name")
    if not email:
        missing.append("email")
    if not raw_date:
        missing.append("date")
    if not raw_time:
        missing.append("time")

    if missing:
        return {
            "error": True,
            "message": f"Missing fields: {', '.join(missing)}",
            "extracted": extracted
        }

    normalized = normalize_date_time(raw_date, raw_time)
    if not normalized:
        return {
            "error": True,
            "message": "Invalid or unparseable date/time.",
            "extracted": extracted
        }
    normalized_date, normalized_time = normalized

    meeting_datetime = datetime.strptime(
        f"{normalized_date} {normalized_time}",
        "%Y-%m-%d %H:%M"
    )

    booking = Booking(
        session_id=user_id,
        name=name,
        email=email,
        meeting_datetime=meeting_datetime,
        notes=user_text,
    )

    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)
    except Exception as exc:
        db.rollback()
        return {
            "error": True,
            "message": f"Failed to persist booking: {exc}",
            "extracted": extracted
        }

    return {
        "error": False,
        "booking_id": booking.id,
        "name": name,
        "email": email,
        "datetime": meeting_datetime,
    }
