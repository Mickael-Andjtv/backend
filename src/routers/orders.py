from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
import uuid
from datetime import datetime

from ..models import Order, OrderItem, MenuItem, Customer, PromoCode
from ..schemas import (
    OrderCreateSchema,
    OrderUpdateSchema,
    OrderStatusUpdateSchema,
    OrderResponseSchema,
)
from ..core.database import get_session

router = APIRouter(prefix="/api/orders", tags=["orders"])


def generate_order_number(session: Session) -> str:
    """Generate a unique order number"""
    count = session.exec(select(Order)).all()
    return f"CMD-{str(len(count) + 1).zfill(3)}"


@router.get("", response_model=list[OrderResponseSchema])
def get_orders(
    session: Session = Depends(get_session),
    status: str = Query(None),
    customer_id: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
):
    """Get all orders"""
    query = select(Order)
    if status:
        query = query.where(Order.status == status)
    if customer_id:
        query = query.where(Order.customerId == customer_id)
    
    orders = session.exec(query.offset(skip).limit(limit)).all()
    return orders


@router.get("/{order_id}", response_model=OrderResponseSchema)
def get_order(order_id: str, session: Session = Depends(get_session)):
    """Get a specific order"""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("", response_model=OrderResponseSchema)
def create_order(
    data: OrderCreateSchema, session: Session = Depends(get_session)
):
    """Create a new order"""
    # Validate customer exists
    customer = session.get(Customer, data.customerId)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Calculate total and validate items
    total_amount = 0.0
    order_items = []
    
    for item_data in data.items:
        menu_item = session.get(MenuItem, item_data.menuItemId)
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item {item_data.menuItemId} not found")
        
        item_total = menu_item.price * item_data.quantity
        total_amount += item_total
        
        order_item = OrderItem(
            id=str(uuid.uuid4()),
            menuItemId=item_data.menuItemId,
            quantity=item_data.quantity,
            totalPrice=item_total,
            notes=item_data.notes,
        )
        order_items.append(order_item)

    # Apply promo code if provided
    discount_amount = 0.0
    if data.appliedPromoId:
        promo = session.get(PromoCode, data.appliedPromoId)
        if promo and promo.isActive:
            if promo.discountType == "PERCENTAGE":
                discount_amount = total_amount * (promo.discountValue / 100)
            else:
                discount_amount = promo.discountValue
            
            if promo.maxDiscountAmount:
                discount_amount = min(discount_amount, promo.maxDiscountAmount)
            
            total_amount -= discount_amount

    # Calculate tax (assuming 20% for example)
    tax_amount = total_amount * 0.2
    final_total = total_amount + tax_amount

    order = Order(
        id=str(uuid.uuid4()),
        orderNumber=generate_order_number(session),
        type=data.type,
        status="PENDING",
        customerId=data.customerId,
        tableId=data.tableId,
        discountAmount=discount_amount,
        appliedPromoId=data.appliedPromoId,
        taxAmount=tax_amount,
        totalAmount=final_total,
        paymentStatus="UNPAID",
        paymentMethod=data.paymentMethod,
        estimatedPreparationTimeMinutes=data.estimatedPreparationTimeMinutes,
    )
    
    session.add(order)
    session.flush()
    
    # Add order items
    for item in order_items:
        item.orderId = order.id
        session.add(item)

    session.commit()
    session.refresh(order)
    return order


@router.put("/{order_id}", response_model=OrderResponseSchema)
def update_order(
    order_id: str,
    data: OrderUpdateSchema,
    session: Session = Depends(get_session),
):
    """Update an order"""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(order, key, value)
    
    order.updatedAt = datetime.utcnow()
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: str,
    data: OrderStatusUpdateSchema,
    session: Session = Depends(get_session),
):
    """Update order status"""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = data.status
    
    # Set completed time if order is completed
    if data.status == "COMPLETED":
        order.completedAt = datetime.utcnow()
    
    order.updatedAt = datetime.utcnow()
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.delete("/{order_id}")
def cancel_order(order_id: str, session: Session = Depends(get_session)):
    """Cancel an order"""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status in ["COMPLETED", "CANCELLED"]:
        raise HTTPException(status_code=400, detail="Cannot cancel a completed or already cancelled order")

    order.status = "CANCELLED"
    order.updatedAt = datetime.utcnow()
    session.add(order)
    session.commit()
    return {"message": "Order cancelled"}
