from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class LoyaltyTier(str, Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    VIP = "VIP"


class CustomerStatus(str, Enum):
    REGULAR = "REGULAR"
    VIP = "VIP"
    BLOCKED = "BLOCKED"


class CustomerLoyaltySchema(BaseModel):
    points: int = 0
    tier: LoyaltyTier = LoyaltyTier.BRONZE
    customDiscountPercent: Optional[float] = None


class CustomerPreferencesSchema(BaseModel):
    isVegetarian: bool = False
    isGlutenFree: bool = False
    allergies: Optional[list[str]] = None
    preferredTableNotes: Optional[str] = None


class CustomerCreateSchema(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    phone: str
    image: Optional[str] = None
    preferences: Optional[CustomerPreferencesSchema] = None


class CustomerUpdateSchema(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    phone: Optional[str] = None
    image: Optional[str] = None
    status: Optional[CustomerStatus] = None
    preferences: Optional[CustomerPreferencesSchema] = None


class CustomerResponseSchema(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    phone: str
    image: Optional[str] = None
    status: CustomerStatus
    loyalty: CustomerLoyaltySchema
    preferences: Optional[CustomerPreferencesSchema] = None
    totalOrders: int
    totalReservations: int
    noShowCount: int
    totalSpent: float
    lastVisitAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
