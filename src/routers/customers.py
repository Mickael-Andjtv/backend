from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
import uuid
from datetime import datetime

from ..models import Customer, CustomerLoyalty, CustomerPreferences
from ..schemas import (
    CustomerCreateSchema,
    CustomerUpdateSchema,
    CustomerResponseSchema,
)
from ..core.database import get_session

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=list[CustomerResponseSchema])
def get_customers(
    session: Session = Depends(get_session),
    status: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(10),
):
    """Get all customers"""
    query = select(Customer)
    if status:
        query = query.where(Customer.status == status)
    
    customers = session.exec(query.offset(skip).limit(limit)).all()
    return customers


@router.get("/{customer_id}", response_model=CustomerResponseSchema)
def get_customer(customer_id: str, session: Session = Depends(get_session)):
    """Get a specific customer"""
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("", response_model=CustomerResponseSchema)
def create_customer(
    data: CustomerCreateSchema, session: Session = Depends(get_session)
):
    """Create a new customer"""
    # Check if customer with same email already exists
    existing = session.exec(
        select(Customer).where(Customer.email == data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    customer_id = str(uuid.uuid4())
    
    customer = Customer(
        id=customer_id,
        firstName=data.firstName,
        lastName=data.lastName,
        email=data.email,
        phone=data.phone,
        image=data.image,
        status="REGULAR",
        totalOrders=0,
        totalReservations=0,
        noShowCount=0,
        totalSpent=0.0,
    )
    
    # Create loyalty record
    loyalty = CustomerLoyalty(
        id=str(uuid.uuid4()),
        customerId=customer_id,
        points=0,
        tier="BRONZE",
    )
    
    # Create preferences if provided
    if data.preferences:
        preferences = CustomerPreferences(
            id=str(uuid.uuid4()),
            customerId=customer_id,
            isVegetarian=data.preferences.isVegetarian,
            isGlutenFree=data.preferences.isGlutenFree,
            allergies=data.preferences.allergies or [],
            preferredTableNotes=data.preferences.preferredTableNotes,
        )
        session.add(preferences)
    
    session.add(customer)
    session.add(loyalty)
    session.commit()
    session.refresh(customer)
    return customer


@router.put("/{customer_id}", response_model=CustomerResponseSchema)
def update_customer(
    customer_id: str,
    data: CustomerUpdateSchema,
    session: Session = Depends(get_session),
):
    """Update a customer"""
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    update_data = data.model_dump(exclude_unset=True)
    
    # Handle preferences separately
    preferences_data = update_data.pop("preferences", None)
    
    for key, value in update_data.items():
        setattr(customer, key, value)
    
    # Update preferences if provided
    if preferences_data:
        prefs = session.exec(
            select(CustomerPreferences).where(CustomerPreferences.customerId == customer_id)
        ).first()
        if prefs:
            prefs.isVegetarian = preferences_data.get("isVegetarian", prefs.isVegetarian)
            prefs.isGlutenFree = preferences_data.get("isGlutenFree", prefs.isGlutenFree)
            if preferences_data.get("allergies"):
                prefs.allergies = preferences_data["allergies"]
            prefs.preferredTableNotes = preferences_data.get("preferredTableNotes", prefs.preferredTableNotes)
            session.add(prefs)
    
    customer.updatedAt = datetime.utcnow()
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.delete("/{customer_id}")
def delete_customer(customer_id: str, session: Session = Depends(get_session)):
    """Delete a customer (soft delete via status)"""
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer.status = "BLOCKED"
    customer.updatedAt = datetime.utcnow()
    session.add(customer)
    session.commit()
    return {"message": "Customer deactivated"}


@router.patch("/{customer_id}/loyalty")
def update_loyalty(
    customer_id: str,
    points: int = Query(...),
    session: Session = Depends(get_session),
):
    """Update customer loyalty points"""
    loyalty = session.exec(
        select(CustomerLoyalty).where(CustomerLoyalty.customerId == customer_id)
    ).first()
    if not loyalty:
        raise HTTPException(status_code=404, detail="Customer loyalty not found")

    loyalty.points += points
    
    # Update tier based on points
    if loyalty.points >= 3000:
        loyalty.tier = "VIP"
    elif loyalty.points >= 2000:
        loyalty.tier = "GOLD"
    elif loyalty.points >= 1000:
        loyalty.tier = "SILVER"
    else:
        loyalty.tier = "BRONZE"
    
    session.add(loyalty)
    session.commit()
    session.refresh(loyalty)
    return loyalty
