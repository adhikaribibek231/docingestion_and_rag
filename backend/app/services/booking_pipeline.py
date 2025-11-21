import json
from datetime import datetime

from sqlmodel import Session

from app.core.redis_client import redis_client
from app.models.booking import Booking
from app.services.booking_extractor import extract_booking_info
from app.services.date_normalizer import normalize_date_time

BOOKING_DRAFT_PREFIX = "booking_draft:"


def _load_draft(session_id: str) -> dict:
    if redis_client is None:
        return {}
    try:
        raw = redis_client.get(f"{BOOKING_DRAFT_PREFIX}{session_id}")
        return json.loads(raw) if raw else {}
    except Exception as exc:
        print(f"Failed to load booking draft: {exc}")
        return {}


def _save_draft(session_id: str, data: dict):
    if redis_client is None:
        return
    try:
        redis_client.set(f"{BOOKING_DRAFT_PREFIX}{session_id}", json.dumps(data), ex=60 * 60)
    except Exception as exc:
        print(f"Failed to save booking draft: {exc}")


def _clear_draft(session_id: str):
    if redis_client is None:
        return
    try:
        redis_client.delete(f"{BOOKING_DRAFT_PREFIX}{session_id}")
    except Exception as exc:
        print(f"Failed to clear booking draft: {exc}")


def has_booking_draft(session_id: str) -> bool:
    draft = _load_draft(session_id)
    return bool(draft)


def _missing_message(missing: list[str]) -> str:
    labels = {
        "name": "your name",
        "email": "your email",
        "date": "the appointment date",
        "time": "the appointment time",
    }
    parts = [labels[m] for m in missing if m in labels]
    if not parts:
        return "I'm sorry, I need a bit more info to book this."
    if len(parts) == 1:
        return f"I’m sorry, I didn’t get {parts[0]}. Could you share it?"
    return f"I’m sorry, I didn’t get {', '.join(parts[:-1])} or {parts[-1]}. Could you share them?"


async def handle_booking(user_id: str, user_text: str, db: Session):
    # Merge this turn with any prior partial info for the session.
    draft = _load_draft(user_id)
    extracted = await extract_booking_info(user_text)

    merged = {
        "name": extracted.get("name") or draft.get("name"),
        "email": extracted.get("email") or draft.get("email"),
        "date": extracted.get("date") or draft.get("date"),
        "time": extracted.get("time") or draft.get("time"),
    }

    missing = [field for field, value in merged.items() if not value]
    if missing:
        _save_draft(user_id, merged)
        return {
            "error": True,
            "message": _missing_message(missing),
            "missing": missing,
            "collected": merged,
        }

    normalized = normalize_date_time(merged["date"], merged["time"])
    if not normalized:
        _save_draft(user_id, merged)
        return {
            "error": True,
            "message": "I couldn’t understand the appointment date/time. Please share the day and time, e.g. 'next Friday at 3pm'.",
            "missing": ["date", "time"],
            "collected": merged,
        }
    normalized_date, normalized_time = normalized

    meeting_datetime = datetime.strptime(
        f"{normalized_date} {normalized_time}",
        "%Y-%m-%d %H:%M"
    )

    booking = Booking(
        session_id=user_id,
        name=merged["name"],
        email=merged["email"],
        meeting_datetime=meeting_datetime,
        notes=user_text,
    )

    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)
    except Exception as exc:
        db.rollback()
        _save_draft(user_id, merged)
        return {
            "error": True,
            "message": f"Failed to persist booking: {exc}",
            "collected": merged
        }

    _clear_draft(user_id)
    return {
        "error": False,
        "booking_id": booking.id,
        "name": merged["name"],
        "email": merged["email"],
        "datetime": meeting_datetime,
    }
