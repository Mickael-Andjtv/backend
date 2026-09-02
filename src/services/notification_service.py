import uuid
from datetime import datetime

from sqlmodel import Session, select

from ..models import Notification


def create_notification(
    session: Session,
    *,
    title: str,
    message: str,
    type: str = "INFO",
    referenceId: str | None = None,
    referenceType: str | None = None,
) -> Notification:
    """Create and persist a notification, then return it (committed)."""
    notification = Notification(
        id=str(uuid.uuid4()),
        title=title,
        message=message,
        type=type,
        referenceId=referenceId,
        referenceType=referenceType,
        isRead=False,
        createdAt=datetime.utcnow(),
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


def get_unread_count(session: Session) -> int:
    notifications = session.exec(select(Notification)).all()
    return sum(1 for n in notifications if not n.isRead)
