from sqlmodel import Session
from datetime import datetime
from app.models.booking import Booking
from app.services.booking_extractor import extract_booking_info
from app.services.date_normalizer import normalize_date_time


async def handle_booking(user_id: str, user_text: str, db: Session):
    # 1. Extract raw name/email/date/time from DeepSeek
    extracted = await extract_booking_info(user_text)

    name = extracted.get("name")
    email = extracted.get("email")
    raw_date = extracted.get("date")
    raw_time = extracted.get("time")

    # 2. Check for missing fields
    missing = []
    if not name: missing.append("name")
    if not email: missing.append("email")
    if not raw_date: missing.append("date")
    if not raw_time: missing.append("time")

    if missing:
        return {
            "error": True,
            "message": f"Missing fields: {', '.join(missing)}",
            "extracted": extracted
        }

    # 3. Normalize natural-language date/time → ISO
    # 3. Normalize → returns ("YYYY-MM-DD", "HH:MM")
    normalized_date, normalized_time = normalize_date_time(raw_date, raw_time)

    if not normalized_date or not normalized_time:
        return {
            "error": True,
            "message": "Invalid or unparseable date/time.",
            "extracted": extracted
        }

    # 4. Convert to real datetime object for SQLite
    meeting_datetime = datetime.strptime(
        f"{normalized_date} {normalized_time}",
        "%Y-%m-%d %H:%M"
    )


    # 5. Save booking
    booking = Booking(
        session_id=user_id,
        name=name,
        email=email,
        meeting_datetime=meeting_datetime,
        notes=user_text,
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
