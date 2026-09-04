from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User
from app.repositories import (
    ticket_history_repository,
    ticket_repository
)


def add_history(
    db: Session,
    ticket_id: int,
    user_id: int,
    action: str,
    description: str
):
    return ticket_history_repository.create_history(
        db=db,
        ticket_id=ticket_id,
        user_id=user_id,
        action=action,
        description=description
    )


def get_ticket_history(
    db: Session,
    ticket_id: int,
    current_user: User
):
    ticket = ticket_repository.get_ticket_by_id(
        db,
        ticket_id
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Admin can view every ticket history
    if current_user.role == "admin":
        return ticket_history_repository.get_ticket_history(
            db,
            ticket_id
        )

    # Assigned support agent can view history
    if current_user.role == "support_agent":
        if ticket.assigned_to != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to view this ticket history"
            )

        return ticket_history_repository.get_ticket_history(
            db,
            ticket_id
        )

    # Customer can only view their own ticket history
    if current_user.role == "customer":
        if not current_user.customer:
            raise HTTPException(
                status_code=403,
                detail="Customer profile not found"
            )

        if ticket.customer_id != current_user.customer.id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to view this ticket history"
            )

        return ticket_history_repository.get_ticket_history(
            db,
            ticket_id
        )

    raise HTTPException(
        status_code=403,
        detail="Access denied"
    )