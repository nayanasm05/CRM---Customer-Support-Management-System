from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User, Notification
from app.repositories import notification_repository


def send_notification(
    db: Session,
    user_id: int,
    message: str
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        return {
            "success": False,
            "message": "User not found"
        }

    return {
        "success": True,
        "user_id": user_id,
        "message": message
    }


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str
):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        is_read=False
    )

    return notification_repository.create_notification(
        db,
        notification
    )


def get_my_notifications(
    db: Session,
    current_user
):
    return notification_repository.get_notifications_by_user(
        db,
        current_user.id
    )


def mark_notification_as_read(
    db: Session,
    notification_id: int,
    current_user
):
    notification = notification_repository.get_notification_by_id(
        db,
        notification_id
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to modify this notification"
        )

    return notification_repository.mark_as_read(
        db,
        notification
    )


def mark_all_notifications_as_read(
    db: Session,
    current_user
):
    notification_repository.mark_all_as_read(
        db,
        current_user.id
    )

    return {
        "message": "All notifications marked as read"
    }


def create_background_notification(
    user_id: int,
    title: str,
    message: str
):
    from app.database import SessionLocal

    db = SessionLocal()

    try:
        create_notification(
            db,
            user_id,
            title,
            message
        )
    finally:
        db.close()