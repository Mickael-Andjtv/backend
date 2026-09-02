from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, and_
import uuid
from datetime import datetime, date

from ..models import Reservation, Customer
from ..schemas import (
    ReservationCreateSchema,
    ReservationUpdateSchema,
    ReservationStatusUpdateSchema,
    ReservationResponseSchema,
)
from ..core.database import get_session
from ..services.notification_service import create_notification

router = APIRouter(prefix="/api/reservations", tags=["reservations"])


@router.get("", response_model=list[ReservationResponseSchema])
def get_reservations(
    session: Session = Depends(get_session),
    status: str = Query(None),
    customer_id: str = Query(None),
    reservation_date: date = Query(None),
    skip: int = Query(0),
    limit: int = Query(500),
):
    """Get all reservations"""
    filters = []
    
    if status:
        filters.append(Reservation.status == status)
    if customer_id:
        filters.append(Reservation.customerId == customer_id)
    if reservation_date:
        filters.append(Reservation.reservationDate == reservation_date)
    
    query = select(Reservation)
    if filters:
        query = query.where(and_(*filters))
    
    reservations = session.exec(query.offset(skip).limit(limit)).all()
    return reservations


@router.get("/{reservation_id}", response_model=ReservationResponseSchema)
def get_reservation(
    reservation_id: str, session: Session = Depends(get_session)
):
    """Get a specific reservation"""
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


@router.post("", response_model=ReservationResponseSchema)
def create_reservation(
    data: ReservationCreateSchema, session: Session = Depends(get_session)
):
    """Create a new reservation"""
    # Validate customer exists
    customer = session.get(Customer, data.customerId)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    reservation = Reservation(
        id=str(uuid.uuid4()),
        customerId=data.customerId,
        tableId=data.tableId,
        reservationDate=data.reservationDate,
        reservationTime=data.reservationTime,
        numberOfGuests=data.numberOfGuests,
        status="PENDING",
        specialRequest=data.specialRequest,
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)

    # Notify admin of the new reservation
    create_notification(
        session,
        title="Nouvelle réservation",
        message=(
            f"{customer.firstName} {customer.lastName} a réservé une table "
            f"pour {data.numberOfGuests} personne(s) le {data.reservationDate} "
            f"à {data.reservationTime}."
        ),
        type="RESERVATION",
        referenceId=reservation.id,
        referenceType="reservation",
    )
    return reservation


@router.put("/{reservation_id}", response_model=ReservationResponseSchema)
def update_reservation(
    reservation_id: str,
    data: ReservationUpdateSchema,
    session: Session = Depends(get_session),
):
    """Update a reservation"""
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(reservation, key, value)
    
    reservation.updatedAt = datetime.utcnow()
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


@router.patch("/{reservation_id}/status", response_model=ReservationResponseSchema)
def update_reservation_status(
    reservation_id: str,
    data: ReservationStatusUpdateSchema,
    session: Session = Depends(get_session),
):
    """Update reservation status"""
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    reservation.status = data.status
    reservation.updatedAt = datetime.utcnow()
    session.add(reservation)
    session.commit()
    session.refresh(reservation)

    # Notify admin of important reservation status changes
    customer = session.get(Customer, reservation.customerId)
    name = (
        f"{customer.firstName} {customer.lastName}"
        if customer
        else reservation.customerId
    )
    status_label = {
        "PENDING": "en attente",
        "CONFIRMED": "confirmée",
        "CANCELLED": "annulée",
        "COMPLETED": "terminée",
    }.get(reservation.status, reservation.status)
    create_notification(
        session,
        title="Mise à jour de réservation",
        message=(
            f"La réservation de {name} du {reservation.reservationDate} "
            f"à {reservation.reservationTime} est maintenant {status_label}."
        ),
        type="RESERVATION",
        referenceId=reservation.id,
        referenceType="reservation",
    )
    return reservation


@router.delete("/{reservation_id}")
def cancel_reservation(
    reservation_id: str, session: Session = Depends(get_session)
):
    """Cancel a reservation"""
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if reservation.status == "COMPLETED":
        raise HTTPException(
            status_code=400, detail="Cannot cancel a completed reservation"
        )

    reservation.status = "CANCELLED"
    reservation.updatedAt = datetime.utcnow()
    session.add(reservation)
    session.commit()
    return {"message": "Reservation cancelled"}
