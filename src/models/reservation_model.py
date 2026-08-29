from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from ..enums import RESERVATIONSTATUS

class Reservation(SQLModel):
    reservation_date: datetime
    reservation_end: datetime
    number_of_guests:int
    status:RESERVATIONSTATUS = RESERVATIONSTATUS.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ReservationDB(Reservation, table=True):
    __tablename__ = 'reservations'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_email:str|None = Field(None, foreign_key='users.email')
