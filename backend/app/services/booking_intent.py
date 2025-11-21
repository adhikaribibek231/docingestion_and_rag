import re


ACTION_KEYWORDS = [
    "book",
    "schedule",
    "set up",
    "arrange",
    "reserve",
    "organize",
]

OBJECT_KEYWORDS = [
    "interview",
    "meeting",
    "appointment",
    "call",
]


def is_booking_request(text: str) -> bool:
    if not text:
        return False

    lowered = text.lower()

    # Look for verbs combined with the meeting/interview nouns in any order.
    for action in ACTION_KEYWORDS:
        for obj in OBJECT_KEYWORDS:
            pattern = rf"\b{re.escape(action)}\b.*\b{obj}\b"
            if re.search(pattern, lowered):
                return True

    # Fallback simple phrases to catch common wording.
    return any(phrase in lowered for phrase in [
        "book me an interview",
        "book an interview",
        "book a meeting",
        "schedule an interview",
        "schedule a meeting",
        "schedule a call",
        "set up a call",
        "set up a meeting",
    ])
