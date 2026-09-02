from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session, select
import uuid

from ..models import AuthAccount, Customer, CustomerLoyalty, CustomerPreferences
from ..schemas import AuthResponseSchema, RegisterSchema, LoginSchema
from ..core.database import get_session
from ..services.auth_service import (
    hash_password,
    verify_password,
    create_token,
    decode_token,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _build_customer(dto, loyalty, preferences):
    return {
        "id": dto.id,
        "firstName": dto.firstName,
        "lastName": dto.lastName,
        "email": dto.email,
        "phone": dto.phone,
        "image": dto.image,
        "status": dto.status,
        "loyalty": {
            "points": loyalty.points if loyalty else 0,
            "tier": loyalty.tier if loyalty else "BRONZE",
            "customDiscountPercent": (
                loyalty.customDiscountPercent if loyalty else None
            ),
        },
        "preferences": (
            {
                "isVegetarian": preferences.isVegetarian if preferences else False,
                "isGlutenFree": preferences.isGlutenFree if preferences else False,
                "allergies": preferences.allergies if preferences else [],
                "preferredTableNotes": (
                    preferences.preferredTableNotes if preferences else None
                ),
            }
            if preferences
            else None
        ),
        "totalOrders": dto.totalOrders,
        "totalReservations": dto.totalReservations,
        "noShowCount": dto.noShowCount,
        "totalSpent": dto.totalSpent,
        "lastVisitAt": dto.lastVisitAt,
        "createdAt": dto.createdAt,
        "updatedAt": dto.updatedAt,
    }


def _get_customer_with_relations(session: Session, customer_id: str):
    customer = session.get(Customer, customer_id)
    if not customer:
        return None
    loyalty = session.exec(
        select(CustomerLoyalty).where(CustomerLoyalty.customerId == customer_id)
    ).first()
    preferences = session.exec(
        select(CustomerPreferences).where(CustomerPreferences.customerId == customer_id)
    ).first()
    return _build_customer(customer, loyalty, preferences)


@router.post("/register", response_model=AuthResponseSchema)
def register(
    data: RegisterSchema, session: Session = Depends(get_session)
):
    """Create a client account (credentials linked to a Customer)."""
    existing_account = session.exec(
        select(AuthAccount).where(AuthAccount.email == data.email.lower())
    ).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_customer = session.exec(
        select(Customer).where(Customer.email == data.email.lower())
    ).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Email already registered")

    customer_id = str(uuid.uuid4())
    customer = Customer(
        id=customer_id,
        firstName=data.firstName,
        lastName=data.lastName,
        email=data.email.lower(),
        phone=data.phone or "",
        image=None,
        status="REGULAR",
        totalOrders=0,
        totalReservations=0,
        noShowCount=0,
        totalSpent=0.0,
    )
    loyalty = CustomerLoyalty(
        id=str(uuid.uuid4()),
        customerId=customer_id,
        points=0,
        tier="BRONZE",
    )
    account = AuthAccount(
        id=str(uuid.uuid4()),
        email=data.email.lower(),
        passwordHash=hash_password(data.password),
        customerId=customer_id,
    )

    preferences = None
    if data.preferences:
        preferences = CustomerPreferences(
            id=str(uuid.uuid4()),
            customerId=customer_id,
            isVegetarian=data.preferences.isVegetarian,
            isGlutenFree=data.preferences.isGlutenFree,
            allergies=data.preferences.allergies or [],
            preferredTableNotes=data.preferences.preferredTableNotes,
        )

    session.add(customer)
    session.add(loyalty)
    session.add(account)
    if preferences:
        session.add(preferences)
    session.commit()
    session.refresh(customer)
    session.refresh(loyalty)

    payload = _build_customer(customer, loyalty, preferences)
    token = create_token(customer_id, customer.email)
    return {"token": token, "customer": payload}


@router.post("/login", response_model=AuthResponseSchema)
def login(
    data: LoginSchema, session: Session = Depends(get_session)
):
    """Authenticate a client and return a token."""
    account = session.exec(
        select(AuthAccount).where(AuthAccount.email == data.email.lower())
    ).first()
    if not account or not verify_password(data.password, account.passwordHash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    customer = session.get(Customer, account.customerId)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    payload = _get_customer_with_relations(session, customer.id)
    token = create_token(customer.id, customer.email)
    return {"token": token, "customer": payload}


def get_bearer_token(authorization: str = Header(None)) -> str:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return ""


@router.get("/me", response_model=AuthResponseSchema)
def me(
    session: Session = Depends(get_session),
    token: str = Depends(get_bearer_token),
):
    """Return the current logged-in customer."""
    customer_id = decode_token(token) if token else None
    if not customer_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    payload = _get_customer_with_relations(session, customer.id)
    return {"token": token, "customer": payload}


def get_current_customer_id(
    session: Session = Depends(get_session),
    token: str = Depends(get_bearer_token),
) -> str:
    """FastAPI dependency returning the authenticated customer id."""
    customer_id = decode_token(token) if token else None
    if not customer_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return customer_id