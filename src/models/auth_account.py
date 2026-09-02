from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class AuthAccount(SQLModel, table=True):
    __tablename__ = "auth_account"

    id: Optional[str] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    passwordHash: str
    customerId: str = Field(foreign_key="customer.id", unique=True)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    customer: Optional["Customer"] = Relationship()