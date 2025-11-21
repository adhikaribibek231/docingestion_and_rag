from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

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

def parse_time(raw_time: str):
    raw_time = raw_time.lower().strip()

    # 3pm → 15:00
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


def normalize_date_time(raw_date: str, raw_time: str):
    print("\n--- NEW NORMALIZER DEBUG ---")
    print("Raw date:", raw_date)
    print("Raw time:", raw_time)

    now = datetime.now(NP_TZ)

    raw_date = raw_date.lower().strip()

    # 1. Handle explicit weekday phrases
    for word, weekday_num in WEEKDAYS.items():
        if word in raw_date:
            today_weekday = now.weekday()
            days_ahead = (weekday_num - today_weekday) % 7

            # "next Friday" → skip this week
            if "next" in raw_date and days_ahead == 0:
                days_ahead = 7

            # if "next", always move forward at least 1 week
            if "next" in raw_date and days_ahead <= 0:
                days_ahead += 7

            target_date = now + timedelta(days=days_ahead)
            final_date = target_date.strftime("%Y-%m-%d")

            final_time = parse_time(raw_time)
            if not final_time:
                print("TIME FAILED PARSING")
                return None

            print("Parsed date:", final_date)
            print("Parsed time:", final_time)
            return final_date, final_time

    print("NO WEEKDAY FOUND. Cannot parse.")
    return None
