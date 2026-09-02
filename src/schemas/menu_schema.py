from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class ItemStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    HIDDEN = "HIDDEN"


class CategoryCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    imageUrl: Optional[str] = None


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    isActive: Optional[bool] = None


class CategoryResponseSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    isActive: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class MenuOptionSchema(BaseModel):
    id: Optional[str] = None
    name: str
    priceExtra: Optional[float] = 0.0


class MenuOptionGroupSchema(BaseModel):
    id: Optional[str] = None
    name: str
    required: bool = False
    minChoices: Optional[int] = None
    maxChoices: Optional[int] = None
    options: list[MenuOptionSchema] = []


class MenuItemCreateSchema(BaseModel):
    categoryId: str
    name: str
    description: Optional[str] = None
    price: float
    imageUrl: Optional[list[str]] = None
    status: ItemStatus = ItemStatus.AVAILABLE
    isVegetarian: bool = False
    isGlutenFree: bool = False
    preparationTimeMinutes: Optional[int] = None
    optionGroups: Optional[list[MenuOptionGroupSchema]] = None


class MenuItemUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    categoryId: Optional[str] = None
    status: Optional[ItemStatus] = None
    isVegetarian: Optional[bool] = None
    isGlutenFree: Optional[bool] = None
    preparationTimeMinutes: Optional[int] = None
    imageUrl: Optional[list[str]] = None


class MenuItemResponseSchema(BaseModel):
    id: str
    categoryId: str
    name: str
    description: Optional[str] = None
    price: float
    imageUrl: Optional[list[str]] = None
    status: ItemStatus
    isVegetarian: bool
    isGlutenFree: bool
    preparationTimeMinutes: Optional[int] = None
    optionGroups: Optional[list[MenuOptionGroupSchema]] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
