from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class OrderType(str, Enum):
    EAT_IN = "EAT_IN"
    TAKEAWAY = "TAKEAWAY"
    DELIVERY = "DELIVERY"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY = "READY"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PaymentStatus(str, Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    REFUNDED = "REFUNDED"


class PaymentMethod(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    MOBILE_MONEY = "MOBILE_MONEY"
    OTHER = "OTHER"


class OrderItemCreateSchema(BaseModel):
    menuItemId: str
    quantity: int
    notes: Optional[str] = None


class OrderItemResponseSchema(BaseModel):
    id: str
    menuItemId: str
    quantity: int
    totalPrice: float
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class OrderCreateSchema(BaseModel):
    type: OrderType
    customerId: str
    tableId: Optional[str] = None
    items: list[OrderItemCreateSchema]
    appliedPromoId: Optional[str] = None
    paymentMethod: Optional[PaymentMethod] = None
    estimatedPreparationTimeMinutes: Optional[int] = None


class OrderUpdateSchema(BaseModel):
    status: Optional[OrderStatus] = None
    paymentStatus: Optional[PaymentStatus] = None
    paymentMethod: Optional[PaymentMethod] = None


class OrderStatusUpdateSchema(BaseModel):
    status: OrderStatus


class OrderResponseSchema(BaseModel):
    id: str
    orderNumber: str
    type: OrderType
    status: OrderStatus
    customerId: str
    tableId: Optional[str] = None
    items: list[OrderItemResponseSchema]
    discountAmount: Optional[float] = 0.0
    appliedPromoId: Optional[str] = None
    taxAmount: Optional[float] = 0.0
    totalAmount: float
    paymentStatus: PaymentStatus
    paymentMethod: Optional[PaymentMethod] = None
    estimatedPreparationTimeMinutes: Optional[int] = None
    completedAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
