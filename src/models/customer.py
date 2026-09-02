from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum
from sqlalchemy import Column, JSON


class LoyaltyTier(str, Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    VIP = "VIP"


class CustomerStatus(str, Enum):
    REGULAR = "REGULAR"
    VIP = "VIP"
    BLOCKED = "BLOCKED"


class CustomerLoyalty(SQLModel, table=True):
    __tablename__ = "customer_loyalty"

    id: Optional[str] = Field(default=None, primary_key=True)
    customerId: str = Field(foreign_key="customer.id", unique=True)
    points: int = 0
    tier: LoyaltyTier = LoyaltyTier.BRONZE
    customDiscountPercent: Optional[float] = None
    
    # Relationship
    customer: Optional["Customer"] = Relationship(back_populates="loyalty")


class CustomerPreferences(SQLModel, table=True):
    __tablename__ = "customer_preferences"

    id: Optional[str] = Field(default=None, primary_key=True)
    customerId: str = Field(foreign_key="customer.id", unique=True)
    isVegetarian: bool = False
    isGlutenFree: bool = False
    allergies: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    preferredTableNotes: Optional[str] = None
    
    # Relationship
    customer: Optional["Customer"] = Relationship(back_populates="preferences")


class Customer(SQLModel, table=True):
    __tablename__ = "customer"

    id: Optional[str] = Field(default=None, primary_key=True)
    firstName: str
    lastName: str
    email: str = Field(unique=True, index=True)
    phone: str
    image: Optional[str] = None
    status: CustomerStatus = CustomerStatus.REGULAR
    
    # Stats
    totalOrders: int = 0
    totalReservations: int = 0
    noShowCount: int = 0
    totalSpent: float = 0.0
    lastVisitAt: Optional[datetime] = None
    
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    loyalty: Optional[CustomerLoyalty] = Relationship(back_populates="customer", sa_relationship_kwargs={"uselist": False})
    preferences: Optional[CustomerPreferences] = Relationship(back_populates="customer", sa_relationship_kwargs={"uselist": False})
    orders: List["Order"] = Relationship(back_populates="customer")
    reservations: List["Reservation"] = Relationship(back_populates="customer")
