from datetime import datetime, date, time
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from ..enums import RESERVATIONSTATUS


class Reservation(SQLModel, table=True):
    __tablename__ = "reservation"

    id: Optional[str] = Field(default=None, primary_key=True)
    customerId: str = Field(foreign_key="customer.id")
    tableId: Optional[str] = Field(None, foreign_key="restaurant_table.id")
    reservationDate: date
    reservationTime: time
    numberOfGuests: int
    status: RESERVATIONSTATUS = RESERVATIONSTATUS.PENDING
    specialRequest: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    customer: Optional["Customer"] = Relationship(back_populates="reservations")
    table: Optional["RestaurantTable"] = Relationship(back_populates="reservations")
