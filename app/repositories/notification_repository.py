from sqlalchemy.orm import Session

from app.models import Notification


def create_notification(
    db: Session,
    notification: Notification
):
    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def get_notifications_by_user(
    db: Session,
    user_id: int
):
    return db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(
        Notification.created_at.desc()
    ).all()


def get_notification_by_id(
    db: Session,
    notification_id: int
):
    return db.query(Notification).filter(
        Notification.id == notification_id
    ).first()


def mark_as_read(
    db: Session,
    notification: Notification
):
    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return notification


def mark_all_as_read(
    db: Session,
    user_id: int
):
    db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update(
        {
            Notification.is_read: True
        },
        synchronize_session=False
    )

    db.commit()