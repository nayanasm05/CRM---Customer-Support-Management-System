from sqlalchemy.orm import Session

from app.models import TicketHistory


def create_history(
    db: Session,
    ticket_id: int,
    user_id: int,
    action: str,
    description: str
):
    history = TicketHistory(
        ticket_id=ticket_id,
        user_id=user_id,
        action=action,
        description=description
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history


def get_ticket_history(
    db: Session,
    ticket_id: int
):
    return (
        db.query(TicketHistory)
        .filter(TicketHistory.ticket_id == ticket_id)
        .order_by(TicketHistory.created_at.desc())
        .all()
    )