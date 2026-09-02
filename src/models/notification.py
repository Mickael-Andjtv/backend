from datetime import datetime
from sqlmodel import SQLModel, Field


class Notification(SQLModel, table=True):
    __tablename__ = "notification"

    id: str = Field(primary_key=True)
    title: str
    message: str
    type: str = "INFO"
    referenceId: str | None = None
    referenceType: str | None = None
    isRead: bool = False
    createdAt: datetime = Field(default_factory=datetime.utcnow)
