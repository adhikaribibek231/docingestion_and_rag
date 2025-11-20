from pydantic import BaseModel

class BookingInfo(BaseModel):
    user_id: str
    name: str | None = None
    email: str | None = None
    date: str | None = None
    time: str | None = None
    notes: str