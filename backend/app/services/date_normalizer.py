import dateparser
from datetime import datetime, timezone


def normalize_date_time(raw_date: str, raw_time: str):

    if not raw_date or not raw_time:
        return None, None


    combined = f"{raw_date} {raw_time}"

    now = datetime.now(timezone.utc)
    parsed = dateparser.parse(
        combined,
        settings={
            "TIMEZONE": "UTC",
            "RETURN_AS_TIMEZONE_AWARE": True,
            "RELATIVE_BASE": now,   # VERY IMPORTANT
            "PREFER_DATES_FROM": "future",
        }
    )

    if parsed is None:
        return None, None


    iso_date = parsed.strftime("%Y-%m-%d")
    iso_time = parsed.strftime("%H:%M")

    return iso_date, iso_time
