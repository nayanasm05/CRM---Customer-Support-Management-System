from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.auth import get_current_user
from app.database import get_db
from app.models import User, Ticket


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("/tickets")
def ticket_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        return {
            "message": "Admin access required"
        }

    total_tickets = db.query(Ticket).count()

    open_tickets = db.query(Ticket).filter(
        Ticket.status == "open"
    ).count()

    closed_tickets = db.query(Ticket).filter(
        Ticket.status == "closed"
    ).count()

    high_priority = db.query(Ticket).filter(
        Ticket.priority == "high"
    ).count()

    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "closed_tickets": closed_tickets,
        "high_priority_tickets": high_priority
    }