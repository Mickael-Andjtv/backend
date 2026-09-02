from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_item"

    id: Optional[str] = Field(default=None, primary_key=True)
    orderId: str = Field(foreign_key="order.id")
    menuItemId: str = Field(foreign_key="menu_item.id")
    quantity: int
    totalPrice: float
    notes: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)