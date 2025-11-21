from datetime import datetime

def build_meeting_datetime(date_str: str, time_str: str):
    if not date_str or not time_str:
        return None

    try:
        combined = f"{date_str} {time_str}"
        dt = datetime.strptime(combined, "%Y-%m-%d %H:%M")
        return dt
    except:
        return None
