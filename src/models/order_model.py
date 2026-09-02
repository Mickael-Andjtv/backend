from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from ..enums import ORDERSTATUS, PAYMENTSTATUS, PAYMENTMETHOD


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_item"

    id: Optional[str] = Field(default=None, primary_key=True)
    orderId: str = Field(foreign_key="order.id")
    menuItemId: str = Field(foreign_key="menu_item.id")
    quantity: int
    totalPrice: float
    notes: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    order: Optional["Order"] = Relationship(back_populates="items")
    menuItem: Optional["MenuItem"] = Relationship()


class Order(SQLModel, table=True):
    __tablename__ = "order"

    id: Optional[str] = Field(default=None, primary_key=True)
    orderNumber: str = Field(unique=True, index=True)
    type: str  # "EAT_IN", "TAKEAWAY", "DELIVERY"
    status: ORDERSTATUS = ORDERSTATUS.PENDING
    customerId: str = Field(foreign_key="customer.id")
    tableId: Optional[str] = Field(None, foreign_key="restaurant_table.id")
    
    # Financial calculations
    discountAmount: Optional[float] = 0.0
    appliedPromoId: Optional[str] = Field(None, foreign_key="promo_code.id")
    taxAmount: Optional[float] = 0.0
    totalAmount: float
    
    # Payment
    paymentStatus: PAYMENTSTATUS = PAYMENTSTATUS.UNPAID
    paymentMethod: Optional[PAYMENTMETHOD] = None
    
    # Timing
    estimatedPreparationTimeMinutes: Optional[int] = None
    completedAt: Optional[datetime] = None
    
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    customer: Optional["Customer"] = Relationship(back_populates="orders")
    table: Optional["RestaurantTable"] = Relationship(back_populates="orders")
    items: List[OrderItem] = Relationship(back_populates="order")
    appliedPromo: Optional["PromoCode"] = Relationship(back_populates="orders")
    