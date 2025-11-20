from pydantic import BaseModel

class BookingRequest(BaseModel):
    user_id: str
    name: str
    email: str
    date: str
    time: str
    notes: str