from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel

class OrderItem(SQLModel):
    quantity:int
    unit_price:float
    subtotal:float
    specialinstruction:str

class OrderItemDB(OrderItem, table=True):
    __tablename__ = 'order_items'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_id:UUID|None = Field(None, foreign_key='orders.id')