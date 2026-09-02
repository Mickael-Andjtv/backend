from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..models import Notification
from ..schemas import (
    NotificationCreateSchema,
    NotificationResponseSchema,
)
from ..core.database import get_session
from ..services.notification_service import (
    create_notification,
    get_unread_count,
)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponseSchema])
def get_notifications(
    session: Session = Depends(get_session),
    unread_only: bool = Query(False),
    skip: int = Query(0),
    limit: int = Query(100),
):
    """Get all notifications (newest first)."""
    query = select(Notification).order_by(Notification.createdAt.desc())
    if unread_only:
        query = query.where(Notification.isRead == False)  # noqa: E712
    notifications = session.exec(query.offset(skip).limit(limit)).all()
    return notifications


@router.get("/unread-count")
def notifications_unread_count(session: Session = Depends(get_session)):
    """Return the number of unread notifications."""
    return {"count": get_unread_count(session)}


@router.post("", response_model=NotificationResponseSchema)
def add_notification(
    data: NotificationCreateSchema,
    session: Session = Depends(get_session),
):
    """Create a notification (also used by internal systems)."""
    return create_notification(
        session,
        title=data.title,
        message=data.message,
        type=data.type,
        referenceId=data.referenceId,
        referenceType=data.referenceType,
    )


@router.patch("/{notification_id}/read", response_model=NotificationResponseSchema)
def mark_notification_read(
    notification_id: str,
    session: Session = Depends(get_session),
):
    """Mark a notification as read."""
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.isRead = True
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


@router.patch("/mark-all-read")
def mark_all_notifications_read(session: Session = Depends(get_session)):
    """Mark every notification as read."""
    notifications = session.exec(select(Notification)).all()
    for notification in notifications:
        notification.isRead = True
        session.add(notification)
    session.commit()
    return {"message": "All notifications marked as read"}
