from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from ..enums import PAYMENTSTATUS, PAYMENTMETHOD


class Payment(SQLModel, table=True):
    __tablename__ = "payment"

    id: Optional[str] = Field(default=None, primary_key=True)
    orderId: str = Field(foreign_key="order.id")
    amount: float
    method: PAYMENTMETHOD = PAYMENTMETHOD.CARD
    status: PAYMENTSTATUS = PAYMENTSTATUS.UNPAID
    transactionId: Optional[str] = None
    paidAt: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    order: Optional["Order"] = Relationship()
