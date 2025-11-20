from datetime import datetime
from sqlmodel import Session
from app.models.booking import Booking
from app.services.booking_extractor import extract_booking_info


async def handle_booking(user_id: str, user_text: str, db: Session):
    extracted = await extract_booking_info(user_text)

    name = extracted.get("name")
    email = extracted.get("email")
    date = extracted.get("date")
    time = extracted.get("time")

    # If DeepSeek fails to extract info
    missing = []
    if not name:
        missing.append("name")
    if not email:
        missing.append("email")
    if not date:
        missing.append("date")
    if not time:
        missing.append("time")

    if missing:
        return {
            "error": True,
            "message": f"Missing fields: {', '.join(missing)}. Please provide them clearly.",
            "extracted": extracted
        }

    # Convert date + time
    try:
        meeting_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    except:
        return {
            "error": True,
            "message": "Invalid date or time format. Use YYYY-MM-DD and HH:MM.",
            "extracted": extracted
        }

    booking = Booking(
        session_id=user_id,
        name=name,
        email=email,
        meeting_datetime=meeting_datetime,
        notes=user_text
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return {
        "error": False,
        "booking_id": booking.id,
        "name": name,
        "email": email,
        "datetime": meeting_datetime,
    }
