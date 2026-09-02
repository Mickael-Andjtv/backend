from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class PromoCode(SQLModel, table=True):
    __tablename__ = "promo_code"

    id: Optional[str] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)
    description: Optional[str] = None
    discountType: str  # "PERCENTAGE" or "FIXED_AMOUNT"
    discountValue: float
    minOrderAmount: Optional[float] = None
    maxDiscountAmount: Optional[float] = None
    
    # Loyalty requirement
    requiredLoyaltyTier: Optional[str] = None  # "BRONZE", "SILVER", "GOLD", "VIP"
    
    # Date range
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    
    # Usage limits
    usageLimit: Optional[int] = None
    usageCount: int = 0
    isForSingleUse: bool = False
    isActive: bool = True
    
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    orders: List["Order"] = Relationship(back_populates="appliedPromo")
