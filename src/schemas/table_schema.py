from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class TableStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    UNAVAILABLE = "UNAVAILABLE"


class TableCreateSchema(BaseModel):
    num: int
    capacity: int
    place: str


class TableUpdateSchema(BaseModel):
    num: Optional[int] = None
    capacity: Optional[int] = None
    place: Optional[str] = None
    status: Optional[TableStatus] = None


class TableResponseSchema(BaseModel):
    id: str
    num: int
    capacity: int
    place: str
    status: TableStatus
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
