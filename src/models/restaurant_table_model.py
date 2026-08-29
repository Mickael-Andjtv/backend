from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from ..enums import TABLESTATUS

class RestaurantTable(SQLModel):
    table_number:int
    capacity:int
    status:TABLESTATUS = TABLESTATUS.AVALAIBLE
    guest_email:str|None = Field(None, foreign_key='users.email')
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class RestaurantTableDB(RestaurantTable, table=True):
    __tablename__ = 'restaurant_tables'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    