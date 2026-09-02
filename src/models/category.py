from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class Category(SQLModel, table=True):
    __tablename__ = "category"

    id: Optional[str] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    isActive: bool = True
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    menuItems: List["MenuItem"] = Relationship(back_populates="category")
