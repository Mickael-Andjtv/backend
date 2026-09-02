from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, time
from enum import Enum


class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class ReservationCreateSchema(BaseModel):
    customerId: str
    reservationDate: date
    reservationTime: time
    numberOfGuests: int
    tableId: Optional[str] = None
    specialRequest: Optional[str] = None


class ReservationUpdateSchema(BaseModel):
    reservationDate: Optional[date] = None
    reservationTime: Optional[time] = None
    numberOfGuests: Optional[int] = None
    tableId: Optional[str] = None
    status: Optional[ReservationStatus] = None
    specialRequest: Optional[str] = None


class ReservationStatusUpdateSchema(BaseModel):
    status: ReservationStatus


class ReservationResponseSchema(BaseModel):
    id: str
    customerId: str
    tableId: Optional[str] = None
    reservationDate: date
    reservationTime: time
    numberOfGuests: int
    status: ReservationStatus
    specialRequest: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
