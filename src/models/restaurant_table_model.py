from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from ..enums import TABLESTATUS


class RestaurantTable(SQLModel, table=True):
    __tablename__ = "restaurant_table"

    id: Optional[str] = Field(default=None, primary_key=True)
    num: int = Field(unique=True, index=True)
    capacity: int
    place: str
    status: TABLESTATUS = TABLESTATUS.AVAILABLE
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    reservations: List["Reservation"] = Relationship(back_populates="table")
    orders: List["Order"] = Relationship(back_populates="table")
    