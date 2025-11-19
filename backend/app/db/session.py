from sqlmodel import Field, SQLModel, create_engine
from app.core.config import settings
engine = create_engine(settings.database_url, echo=True)

def init_db():
    from app.models.document import Document
    from app.models.booking import Booking
    SQLModel.metadata.create_all(engine)