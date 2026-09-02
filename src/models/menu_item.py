from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum
from sqlalchemy import Column, JSON


class ItemStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    HIDDEN = "HIDDEN"


class MenuOption(SQLModel, table=True):
    __tablename__ = "menu_option"

    id: Optional[str] = Field(default=None, primary_key=True)
    optionGroupId: str = Field(foreign_key="menu_option_group.id")
    name: str
    priceExtra: Optional[float] = 0.0
    isActive: bool = True
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    optionGroup: Optional["MenuOptionGroup"] = Relationship(back_populates="options")


class MenuOptionGroup(SQLModel, table=True):
    __tablename__ = "menu_option_group"

    id: Optional[str] = Field(default=None, primary_key=True)
    menuItemId: str = Field(foreign_key="menu_item.id")
    name: str
    required: bool = False
    minChoices: Optional[int] = None
    maxChoices: Optional[int] = None
    isActive: bool = True
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    menuItem: Optional["MenuItem"] = Relationship(back_populates="optionGroups")
    options: List[MenuOption] = Relationship(back_populates="optionGroup")


class MenuItem(SQLModel, table=True):
    __tablename__ = "menu_item"

    id: Optional[str] = Field(default=None, primary_key=True)
    categoryId: str = Field(foreign_key="category.id")
    name: str = Field(index=True)
    description: Optional[str] = None
    price: float
    imageUrl: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: ItemStatus = ItemStatus.AVAILABLE
    isVegetarian: bool = False
    isGlutenFree: bool = False
    preparationTimeMinutes: Optional[int] = None
    isActive: bool = True
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    category: Optional["Category"] = Relationship(back_populates="menuItems")
    optionGroups: List[MenuOptionGroup] = Relationship(back_populates="menuItem")
    orderItems: List["OrderItem"] = Relationship(back_populates="menuItem")
    