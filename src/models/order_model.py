from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from ..enums import ORDERSTATUS


class Order(SQLModel):
    order_number:str
    status:ORDERSTATUS = ORDERSTATUS.PENDING
    total_price:float

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class OrderDB(Order, table=True):
    __tablename__ = 'orders'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    retaurant_id:UUID|None = Field(None, foreign_key='restaurant_tables.id')
    user_email:str|None = Field(None, foreign_key='users.email')
    