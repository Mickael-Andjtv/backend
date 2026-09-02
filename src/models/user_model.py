from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from ..enums import USERROLE


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[str] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password: str
    firstName: str
    lastName: str
    phone: Optional[str] = None
    address: Optional[str] = None
    role: USERROLE = USERROLE.ADMIN
    isActive: bool = True
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    