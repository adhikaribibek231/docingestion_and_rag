from pydantic import BaseModel

class BookingInfo(BaseModel):
    user_id: str
    name: str
    email: str
    date: str
    time: str
    notes: str