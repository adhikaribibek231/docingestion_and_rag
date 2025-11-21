def is_booking_request(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in [
        "book interview",
        "schedule interview",
        "set up meeting",
        "schedule a meeting",
        "appointment",
        "interview at",
    ])
