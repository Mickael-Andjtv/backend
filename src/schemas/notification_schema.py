from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationCreateSchema(BaseModel):
    title: str
    message: str
    type: str = "INFO"
    referenceId: Optional[str] = None
    referenceType: Optional[str] = None


class NotificationResponseSchema(BaseModel):
    id: str
    title: str
    message: str
    type: str
    referenceId: Optional[str] = None
    referenceType: Optional[str] = None
    isRead: bool
    createdAt: datetime

    class Config:
        from_attributes = True
