from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models import User
from app.services import dashboard_service
from app.models import User, Ticket, Customer

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/admin")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can access admin dashboard"
        )

    return dashboard_service.get_admin_dashboard(db)

@router.get("/agent")
def agent_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "support_agent":
        raise HTTPException(
            status_code=403,
            detail="Only support agents can access agent dashboard"
        )

    tickets = (
        db.query(Ticket)
        .filter(Ticket.assigned_to == current_user.id)
        .all()
    )

    return {
        "agent_id": current_user.id,
        "agent_name": current_user.name,
        "total_assigned_tickets": len(tickets),
        "open_tickets": sum(t.status == "open" for t in tickets),
        "in_progress_tickets": sum(
            t.status == "in_progress" for t in tickets
        ),
        "waiting_for_customer_tickets": sum(
            t.status == "waiting_for_customer" for t in tickets
        ),
        "resolved_tickets": sum(
            t.status == "resolved" for t in tickets
        ),
        "closed_tickets": sum(
            t.status == "closed" for t in tickets
        ),
        "critical_tickets": sum(
            t.priority == "critical" for t in tickets
        )
    }
    
@router.get("/customer")
def customer_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=403,
            detail="Only customers can access customer dashboard"
        )

    customer = (
        db.query(Customer)
        .filter(Customer.user_id == current_user.id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer profile not found"
        )

    tickets = (
        db.query(Ticket)
        .filter(Ticket.customer_id == customer.id)
        .all()
    )

    return {
        "customer_id": customer.id,
        "customer_name": current_user.name,
        "total_tickets": len(tickets),
        "open_tickets": sum(t.status == "open" for t in tickets),
        "in_progress_tickets": sum(
            t.status == "in_progress" for t in tickets
        ),
        "waiting_for_customer_tickets": sum(
            t.status == "waiting_for_customer" for t in tickets
        ),
        "resolved_tickets": sum(
            t.status == "resolved" for t in tickets
        ),
        "closed_tickets": sum(
            t.status == "closed" for t in tickets
        ),
        "cancelled_tickets": sum(
            t.status == "cancelled" for t in tickets
        )
    }