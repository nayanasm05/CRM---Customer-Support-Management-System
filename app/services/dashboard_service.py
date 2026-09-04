from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import User, Customer, Ticket, SLATracking


def get_admin_dashboard(db: Session):

    total_customers = db.query(Customer).count()

    active_customers = (
        db.query(Customer)
        .filter(Customer.status == "active")
        .count()
    )

    total_tickets = db.query(Ticket).count()

    open_tickets = (
        db.query(Ticket)
        .filter(Ticket.status == "open")
        .count()
    )

    in_progress_tickets = (
        db.query(Ticket)
        .filter(Ticket.status == "in_progress")
        .count()
    )

    waiting_for_customer_tickets = (
        db.query(Ticket)
        .filter(Ticket.status == "waiting_for_customer")
        .count()
    )

    resolved_tickets = (
        db.query(Ticket)
        .filter(Ticket.status == "resolved")
        .count()
    )

    closed_tickets = (
        db.query(Ticket)
        .filter(Ticket.status == "closed")
        .count()
    )

    cancelled_tickets = (
        db.query(Ticket)
        .filter(Ticket.status == "cancelled")
        .count()
    )

    unassigned_tickets = (
        db.query(Ticket)
        .filter(Ticket.assigned_to.is_(None))
        .count()
    )

    critical_tickets = (
        db.query(Ticket)
        .filter(Ticket.priority == "critical")
        .count()
    )

    breached_sla = (
        db.query(SLATracking)
        .filter(SLATracking.status == "Breached")
        .count()
    )

    at_risk_sla = (
        db.query(SLATracking)
        .filter(SLATracking.status == "At Risk")
        .count()
    )

    total_agents = (
        db.query(User)
        .filter(User.role == "support_agent")
        .count()
    )

    active_agents = (
        db.query(User)
        .filter(
            User.role == "support_agent",
            User.is_active == True
        )
        .count()
    )

    return {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "in_progress_tickets": in_progress_tickets,
        "waiting_for_customer_tickets": waiting_for_customer_tickets,
        "resolved_tickets": resolved_tickets,
        "closed_tickets": closed_tickets,
        "cancelled_tickets": cancelled_tickets,
        "unassigned_tickets": unassigned_tickets,
        "critical_tickets": critical_tickets,
        "breached_sla": breached_sla,
        "at_risk_sla": at_risk_sla,
        "total_agents": total_agents,
        "active_agents": active_agents
    }