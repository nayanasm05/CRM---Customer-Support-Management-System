from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import Ticket, User, Category


def get_ticket_by_id(
    db: Session,
    ticket_id: int
):
    return db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()


def get_tickets(
    db: Session,
    search: str = None,
    status: str = None,
    priority: str = None,
    category_id: int = None,
    assigned_agent_id: int = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    query = db.query(Ticket)

    # Search by subject or description
    if search:
        query = query.filter(
            or_(
                Ticket.subject.ilike(f"%{search}%"),
                Ticket.description.ilike(f"%{search}%")
            )
        )

    # Filter by status
    if status:
        query = query.filter(
            Ticket.status == status
        )

    # Filter by priority
    if priority:
        query = query.filter(
            Ticket.priority == priority
        )

    # Filter by category
    if category_id:
        query = query.filter(
            Ticket.category_id == category_id
        )

    # Filter by assigned agent
    if assigned_agent_id:
        query = query.filter(
            Ticket.assigned_to == assigned_agent_id
        )

    # Sorting
    sort_column = {
        "id": Ticket.id,
        "subject": Ticket.subject,
        "priority": Ticket.priority,
        "status": Ticket.status,
        "created_at": Ticket.created_at,
        "updated_at": Ticket.updated_at
    }.get(sort_by)

    if sort_column is None:
        sort_column = Ticket.created_at

    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Pagination
    offset = (page - 1) * limit

    return query.offset(offset).limit(limit).all()


def get_tickets_by_customer(
    db: Session,
    customer_id: int
):
    return db.query(Ticket).filter(
        Ticket.customer_id == customer_id
    ).all()


def get_user_by_id(
    db: Session,
    user_id: int
):
    return db.query(User).filter(
        User.id == user_id
    ).first()


def create_ticket(
    db: Session,
    ticket_data,
    customer_id: int
):
    ticket = Ticket(
        subject=ticket_data.subject,
        description=ticket_data.description,
        priority=ticket_data.priority,
        customer_id=customer_id,
        category_id=ticket_data.category_id
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket

def delete_ticket(db: Session, ticket):
    db.delete(ticket)
    db.commit()
    
def delete_ticket(db: Session, ticket):
    db.delete(ticket)
    db.commit()
    
def get_assigned_tickets(
    db: Session,
    agent_id: int
):
    return (
        db.query(Ticket)
        .filter(Ticket.assigned_to == agent_id)
        .all()
    )


def get_unassigned_tickets(db: Session):
    return (
        db.query(Ticket)
        .filter(Ticket.assigned_to.is_(None))
        .all()
    )


def get_agent_workload(
    db: Session,
    agent_id: int
):
    return (
        db.query(Ticket)
        .filter(
            Ticket.assigned_to == agent_id,
            Ticket.status.notin_(["closed", "cancelled"])
        )
        .count()
    )