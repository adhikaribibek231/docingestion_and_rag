"""Normalize fuzzy weekday/time phrases into concrete date/time strings."""
import logging
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

NP_TZ = ZoneInfo("Asia/Kathmandu")

# Mapping for weekdays
WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def parse_time(raw_time: str) -> str | None:
    """Convert time strings like '3pm' or '14:30' to 24h HH:MM."""
    raw_time = raw_time.lower().strip()

    # 3pm -> 15:00
    match = re.match(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", raw_time)
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    ampm = match.group(3)

    if ampm == "pm" and hour != 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0

    return f"{hour:02d}:{minute:02d}"


def normalize_date_time(raw_date: str, raw_time: str) -> tuple[str, str] | None:
    """Turn phrases like 'next Friday at 3pm' into a YYYY-MM-DD and HH:MM."""
    logger.debug("Normalizing date/time: %s ; %s", raw_date, raw_time)

    now = datetime.now(NP_TZ)

    raw_date = raw_date.lower().strip()

    # 1. Handle explicit weekday phrases
    for word, weekday_num in WEEKDAYS.items():
        if word in raw_date:
            today_weekday = now.weekday()
            days_ahead = (weekday_num - today_weekday) % 7

            # "next Friday" -> skip this week
            if "next" in raw_date and days_ahead == 0:
                days_ahead = 7

            # if "next", always move forward at least 1 week
            if "next" in raw_date and days_ahead <= 0:
                days_ahead += 7

            target_date = now + timedelta(days=days_ahead)
            final_date = target_date.strftime("%Y-%m-%d")

            final_time = parse_time(raw_time)
            if not final_time:
                logger.info("Time failed parsing for date phrase %s", raw_date)
                return None

            logger.debug("Parsed date/time: %s %s", final_date, final_time)
            return final_date, final_time

    logger.info("No recognizable weekday in phrase '%s'", raw_date)
    return None
