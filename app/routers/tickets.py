from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketReassign
)
from app.auth import get_current_user
from app.services import ticket_service


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


# =========================
# CREATE TICKET
# =========================

@router.post(
    "/",
    response_model=TicketResponse
)
def create_ticket(
    ticket_data: TicketCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ticket_service.create_ticket(
        db,
        ticket_data,
        current_user,
        background_tasks
    )


# =========================
# GET ALL TICKETS
# SEARCH / FILTER / SORT / PAGINATION
# =========================

@router.get(
    "/",
    response_model=list[TicketResponse]
)
def get_tickets(
    search: str = None,
    status: str = None,
    priority: str = None,
    category_id: int = None,
    assigned_agent_id: int = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )

    return ticket_service.get_tickets(
        db,
        search=search,
        status=status,
        priority=priority,
        category_id=category_id,
        assigned_agent_id=assigned_agent_id,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )


# =========================
# ASSIGNED TICKETS
# =========================

@router.get(
    "/assigned/{agent_id}",
    response_model=list[TicketResponse]
)
def get_assigned_tickets(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ticket_service.get_assigned_tickets(
        db,
        agent_id,
        current_user
    )


# =========================
# UNASSIGNED TICKETS
# =========================

@router.get(
    "/unassigned",
    response_model=list[TicketResponse]
)
def get_unassigned_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ticket_service.get_unassigned_tickets(
        db,
        current_user
    )


# =========================
# AGENT WORKLOAD
# =========================

@router.get(
    "/workload/{agent_id}"
)
def get_agent_workload(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ticket_service.get_agent_workload(
        db,
        agent_id,
        current_user
    )


# =========================
# GET TICKET BY ID
# =========================

@router.get(
    "/{ticket_id}",
    response_model=TicketResponse
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ticket_service.get_ticket_by_id(
        db,
        ticket_id,
        current_user
    )


# =========================
# GET CUSTOMER TICKETS
# =========================

@router.get(
    "/customer/{customer_id}",
    response_model=list[TicketResponse]
)
def get_customer_tickets(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ticket_service.get_tickets_by_customer(
        db,
        customer_id
    )


# =========================
# UPDATE TICKET
# =========================

@router.put(
    "/{ticket_id}",
    response_model=TicketResponse
)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ticket_service.update_ticket(
        db,
        ticket_id,
        ticket_data,
        current_user
    )


# =========================
# ASSIGN TICKET
# =========================

@router.put(
    "/{ticket_id}/assign",
    response_model=TicketResponse
)
def assign_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ticket_service.assign_ticket(
        db,
        ticket_id,
        current_user
    )


# =========================
# REASSIGN TICKET
# =========================

@router.put(
    "/{ticket_id}/reassign",
    response_model=TicketResponse
)
def reassign_ticket(
    ticket_id: int,
    ticket_data: TicketReassign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ticket_service.reassign_ticket(
        db,
        ticket_id,
        ticket_data.assigned_to,
        current_user
    )


# =========================
# RESOLVE TICKET
# =========================

@router.put(
    "/{ticket_id}/resolve",
    response_model=TicketResponse
)
def resolve_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ticket_service.resolve_ticket(
        db,
        ticket_id,
        current_user
    )


# =========================
# CLOSE TICKET
# =========================

@router.put(
    "/{ticket_id}/close",
    response_model=TicketResponse
)
def close_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ticket_service.close_ticket(
        db,
        ticket_id,
        current_user
    )


# =========================
# CANCEL TICKET
# =========================

@router.put(
    "/{ticket_id}/cancel",
    response_model=TicketResponse
)
def cancel_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ticket_service.cancel_ticket(
        db,
        ticket_id,
        current_user
    )


# =========================
# DELETE TICKET
# =========================

@router.delete(
    "/{ticket_id}"
)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ticket_service.delete_ticket(
        db,
        ticket_id,
        current_user
    )
