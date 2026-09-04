from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models import Customer, SLATracking
from app.repositories import ticket_repository
from app.models import Customer
from app.services import (
    notification_service,
    sla_service,
    ticket_history_service,
    audit_service
)
# =========================================================
# VALID TICKET STATUS TRANSITIONS
# =========================================================

VALID_STATUS_TRANSITIONS = {
    "open": ["in_progress", "cancelled"],
    "in_progress": [
        "waiting_for_customer",
        "resolved",
        "cancelled"
    ],
    "waiting_for_customer": [
        "in_progress",
        "cancelled"
    ],
    "resolved": ["closed"],
    "closed": [],
    "cancelled": []
}

def get_ticket_by_id(
    db: Session,
    ticket_id: int,
    current_user
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

    if current_user.role == "admin":
        return ticket

    if current_user.role == "support_agent":
        if ticket.assigned_to != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to view this ticket"
            )
        return ticket

    if current_user.role == "customer":
        if not current_user.customer:
            raise HTTPException(
                status_code=403,
                detail="Customer profile not found"
            )

        if ticket.customer_id != current_user.customer.id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to view this ticket"
            )

        return ticket

    raise HTTPException(
        status_code=403,
        detail="Access denied"
    )
# =========================================================
# CREATE TICKET
# =========================================================

def create_ticket(
    db: Session,
    ticket_data,
    current_user,
    background_tasks
):
    customer = db.query(Customer).filter(
        Customer.user_id == current_user.id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=400,
            detail="Customer profile not found for this user"
        )

    ticket = ticket_repository.create_ticket(
        db,
        ticket_data,
        customer.id
    )

    # Create SLA tracking
    sla_service.create_sla_tracking(
        db,
        ticket
    )

    # Create ticket history
    ticket_history_service.add_history(
        db=db,
        ticket_id=ticket.id,
        user_id=current_user.id,
        action="ticket_created",
        description=f"Ticket #{ticket.id} was created"
    )

    # Create audit log
    audit_service.create_audit_log(
        db,
        current_user.id,
        "ticket_created",
        "ticket",
        ticket.id,
        None,
        f"status={ticket.status}, priority={ticket.priority}"
    )

    # Background notification
    background_tasks.add_task(
        notification_service.create_background_notification,
        current_user.id,
        "Ticket Created",
        f"Your ticket #{ticket.id} has been created successfully."
    )

    # Critical ticket background notification
    if ticket.priority == "critical":
        background_tasks.add_task(
            notification_service.create_background_notification,
            current_user.id,
            "Critical Ticket Alert",
            f"Your ticket #{ticket.id} has been created with critical priority."
        )

    return ticket

    
# =========================================================
# UPDATE TICKET
# =========================================================

def update_ticket(
    db: Session,
    ticket_id: int,
    ticket_data,
    current_user
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

    if ticket.status in ["closed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail="Closed or cancelled tickets cannot be updated"
        )

    old_status = ticket.status
    old_priority = ticket.priority
    old_assigned_to = ticket.assigned_to

    # -----------------------------------------------------
    # STATUS UPDATE
    # -----------------------------------------------------

    if ticket_data.status:

        if ticket_data.status not in VALID_STATUS_TRANSITIONS:
            raise HTTPException(
                status_code=400,
                detail="Invalid ticket status"
            )

        if ticket_data.status != ticket.status:

            allowed_statuses = VALID_STATUS_TRANSITIONS[
                ticket.status
            ]

            if ticket_data.status not in allowed_statuses:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Cannot change status from "
                        f"{ticket.status} to "
                        f"{ticket_data.status}"
                    )
                )

            ticket.status = ticket_data.status

            if ticket.status == "resolved":
                ticket.resolved_at = datetime.now(timezone.utc)

    # -----------------------------------------------------
    # PRIORITY UPDATE
    # -----------------------------------------------------

    if ticket_data.priority:

        valid_priorities = [
            "low",
            "medium",
            "high",
            "critical"
        ]

        if ticket_data.priority not in valid_priorities:
            raise HTTPException(
                status_code=400,
                detail="Invalid priority"
            )

        ticket.priority = ticket_data.priority

    # -----------------------------------------------------
    # ASSIGNMENT UPDATE
    # -----------------------------------------------------

    if ticket_data.assigned_to is not None:

        agent = ticket_repository.get_user_by_id(
            db,
            ticket_data.assigned_to
        )

        if not agent:
            raise HTTPException(
                status_code=404,
                detail="Support agent not found"
            )

        if agent.role != "support_agent":
            raise HTTPException(
                status_code=400,
                detail="User is not a support agent"
            )

        if not agent.is_active:
            raise HTTPException(
                status_code=400,
                detail="Inactive support agent cannot be assigned"
            )

        ticket.assigned_to = agent.id

    # -----------------------------------------------------
    # SAVE TICKET
    # -----------------------------------------------------

    db.commit()
    db.refresh(ticket)

    # -----------------------------------------------------
    # CREATE HISTORY
    # -----------------------------------------------------

    if old_status != ticket.status:

        ticket_history_service.add_history(
            db=db,
            ticket_id=ticket.id,
            user_id=current_user.id,
            action="status_changed",
            description=(
                f"Ticket status changed from "
                f"{old_status} to {ticket.status}"
            )
        )

        # Audit log - status change
        audit_service.create_audit_log(
            db,
            current_user.id,
            "ticket_status_changed",
            "ticket",
            ticket.id,
            f"status={old_status}",
            f"status={ticket.status}"
        )

    if old_priority != ticket.priority:

        ticket_history_service.add_history(
            db=db,
            ticket_id=ticket.id,
            user_id=current_user.id,
            action="priority_changed",
            description=(
                f"Ticket priority changed from "
                f"{old_priority} to {ticket.priority}"
            )
        )

        # Audit log - priority change
        audit_service.create_audit_log(
            db,
            current_user.id,
            "ticket_priority_changed",
            "ticket",
            ticket.id,
            f"priority={old_priority}",
            f"priority={ticket.priority}"
        )

    if old_assigned_to != ticket.assigned_to:

        ticket_history_service.add_history(
            db=db,
            ticket_id=ticket.id,
            user_id=current_user.id,
            action="assignment_changed",
            description=(
                f"Ticket assignment changed from "
                f"{old_assigned_to} to "
                f"{ticket.assigned_to}"
            )
        )

        # Audit log - assignment change
        audit_service.create_audit_log(
            db,
            current_user.id,
            "ticket_assignment_changed",
            "ticket",
            ticket.id,
            f"assigned_to={old_assigned_to}",
            f"assigned_to={ticket.assigned_to}"
        )

    # -----------------------------------------------------
    # NOTIFICATION
    # -----------------------------------------------------

    if old_status != ticket.status:

        customer = (
            db.query(Customer)
            .filter(
                Customer.id == ticket.customer_id
            )
            .first()
        )

        if customer:
            notification_service.create_notification(
                db=db,
                user_id=customer.user_id,
                title="Ticket Status Updated",
                message=(
                    f"Your ticket #{ticket.id} status "
                    f"changed from {old_status} "
                    f"to {ticket.status}."
                )
            )

    return ticket

# =========================================================
# REASSIGN TICKET
# =========================================================

def reassign_ticket(
    db: Session,
    ticket_id: int,
    assigned_to: int,
    current_user
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

    if ticket.status in ["closed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"{ticket.status.capitalize()} "
                "tickets cannot be reassigned"
            )
        )

    agent = ticket_repository.get_user_by_id(
        db,
        assigned_to
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found"
        )

    if agent.role != "support_agent":
        raise HTTPException(
            status_code=400,
            detail="Ticket can only be assigned to a support agent"
        )

    if not agent.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot assign ticket to inactive support agent"
        )

    old_agent = ticket.assigned_to

    ticket.assigned_to = agent.id

    db.commit()
    db.refresh(ticket)

    # Create ticket history
    ticket_history_service.add_history(
        db=db,
        ticket_id=ticket.id,
        user_id=current_user.id,
        action="ticket_reassigned",
        description=(
            f"Ticket reassigned from agent "
            f"{old_agent} to agent {agent.id}"
        )
    )

    # Create audit log
    audit_service.create_audit_log(
        db,
        current_user.id,
        "ticket_reassigned",
        "ticket",
        ticket.id,
        f"assigned_to={old_agent}",
        f"assigned_to={agent.id}"
    )

    # Notify new support agent
    notification_service.create_notification(
        db,
        agent.id,
        "Ticket Reassigned",
        f"Ticket #{ticket.id} has been reassigned to you."
    )

    # Notify customer
    customer = db.query(Customer).filter(
        Customer.id == ticket.customer_id
    ).first()

    if customer:
        notification_service.create_notification(
            db,
            customer.user_id,
            "Ticket Reassigned",
            f"Your ticket #{ticket.id} has been reassigned to a support agent."
        )

    return ticket

# =========================================================
# RESOLVE TICKET
# =========================================================

# =========================================================
# RESOLVE TICKET
# =========================================================

def resolve_ticket(
    db: Session,
    ticket_id: int,
    current_user
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

    if ticket.status == "closed":
        raise HTTPException(
            status_code=400,
            detail="Closed tickets cannot be modified"
        )

    if ticket.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Cancelled tickets cannot be modified"
        )

    allowed_next_statuses = VALID_STATUS_TRANSITIONS.get(
        ticket.status,
        []
    )

    if "resolved" not in allowed_next_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status transition: "
                f"{ticket.status} -> resolved"
            )
        )

    # Resolve ticket
    old_status = ticket.status
    resolved_time = datetime.now(timezone.utc)

    ticket.status = "resolved"
    ticket.resolved_at = resolved_time

    # Update SLA tracking
    sla = db.query(SLATracking).filter(
        SLATracking.ticket_id == ticket.id
    ).first()

    if sla:
        created_at = ticket.created_at
        deadline = sla.deadline

        if created_at.tzinfo is None:
            created_at = created_at.replace(
                tzinfo=timezone.utc
            )

        if deadline.tzinfo is None:
            deadline = deadline.replace(
                tzinfo=timezone.utc
            )

        sla.resolved_at = resolved_time

        sla.resolution_time = int(
            (resolved_time - created_at).total_seconds()
        )

        if resolved_time <= deadline:
            sla.status = "Within SLA"
        else:
            sla.status = "Breached"

    db.commit()
    db.refresh(ticket)

    # Create ticket history
    ticket_history_service.add_history(
        db=db,
        ticket_id=ticket.id,
        user_id=current_user.id,
        action="ticket_resolved",
        description=f"Ticket #{ticket.id} was resolved"
    )

    # Create audit log
    audit_service.create_audit_log(
        db,
        current_user.id,
        "ticket_resolved",
        "ticket",
        ticket.id,
        f"status={old_status}",
        "status=resolved"
    )

    # Notify customer
    customer = db.query(Customer).filter(
        Customer.id == ticket.customer_id
    ).first()

    if customer:
        notification_service.create_notification(
            db,
            customer.user_id,
            "Ticket Resolved",
            f"Your ticket #{ticket.id} has been resolved."
        )

    return ticket


# =========================================================
# CLOSE TICKET
# =========================================================

def close_ticket(
    db: Session,
    ticket_id: int,
    current_user
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

    if ticket.status == "closed":
        raise HTTPException(
            status_code=400,
            detail="Ticket is already closed"
        )

    if ticket.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Cancelled tickets cannot be closed"
        )

    allowed_next_statuses = VALID_STATUS_TRANSITIONS.get(
        ticket.status,
        []
    )

    if "closed" not in allowed_next_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status transition: "
                f"{ticket.status} -> closed"
            )
        )

    old_status = ticket.status

    ticket.status = "closed"

    db.commit()
    db.refresh(ticket)

    # Create ticket history
    ticket_history_service.add_history(
        db=db,
        ticket_id=ticket.id,
        user_id=current_user.id,
        action="ticket_closed",
        description=f"Ticket #{ticket.id} was closed"
    )

    # Create audit log
    audit_service.create_audit_log(
        db,
        current_user.id,
        "ticket_closed",
        "ticket",
        ticket.id,
        f"status={old_status}",
        "status=closed"
    )

    # Notify customer
    customer = db.query(Customer).filter(
        Customer.id == ticket.customer_id
    ).first()

    if customer:
        notification_service.create_notification(
            db,
            customer.user_id,
            "Ticket Closed",
            f"Your ticket #{ticket.id} has been closed."
        )

    return ticket
# =========================================================
# CANCEL TICKET
# =========================================================

def cancel_ticket(
    db: Session,
    ticket_id: int,
    current_user
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

    if ticket.status == "closed":
        raise HTTPException(
            status_code=400,
            detail="Closed tickets cannot be cancelled"
        )

    if ticket.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Ticket is already cancelled"
        )

    allowed_next_statuses = VALID_STATUS_TRANSITIONS.get(
        ticket.status,
        []
    )

    if "cancelled" not in allowed_next_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status transition: "
                f"{ticket.status} -> cancelled"
            )
        )

    old_status = ticket.status

    ticket.status = "cancelled"

    db.commit()
    db.refresh(ticket)

    # Create ticket history
    ticket_history_service.add_history(
        db=db,
        ticket_id=ticket.id,
        user_id=current_user.id,
        action="ticket_cancelled",
        description=f"Ticket #{ticket.id} was cancelled"
    )

    # Create audit log
    audit_service.create_audit_log(
        db,
        current_user.id,
        "ticket_cancelled",
        "ticket",
        ticket.id,
        f"status={old_status}",
        "status=cancelled"
    )

    # Notify customer
    customer = db.query(Customer).filter(
        Customer.id == ticket.customer_id
    ).first()

    if customer:
        notification_service.create_notification(
            db,
            customer.user_id,
            "Ticket Cancelled",
            f"Your ticket #{ticket.id} has been cancelled."
        )

    return ticket
    
def get_assigned_tickets(
    db: Session,
    agent_id: int,
    current_user
):
    if current_user.role == "support_agent":
        if current_user.id != agent_id:
            raise HTTPException(
                status_code=403,
                detail="You can only view your own assigned tickets"
            )

    elif current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins and support agents can view assigned tickets"
        )

    agent = ticket_repository.get_user_by_id(db, agent_id)

    if not agent or agent.role != "support_agent":
        raise HTTPException(
            status_code=404,
            detail="Support agent not found"
        )

    return ticket_repository.get_assigned_tickets(
        db,
        agent_id
    )


def get_unassigned_tickets(
    db: Session,
    current_user
):
    if current_user.role not in ["admin", "support_agent"]:
        raise HTTPException(
            status_code=403,
            detail="Only admins and support agents can view unassigned tickets"
        )

    return ticket_repository.get_unassigned_tickets(db)


def get_agent_workload(
    db: Session,
    agent_id: int,
    current_user
):
    if current_user.role == "support_agent":
        if current_user.id != agent_id:
            raise HTTPException(
                status_code=403,
                detail="You can only view your own workload"
            )

    elif current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins and support agents can view agent workload"
        )

    agent = ticket_repository.get_user_by_id(db, agent_id)

    if not agent or agent.role != "support_agent":
        raise HTTPException(
            status_code=404,
            detail="Support agent not found"
        )

    count = ticket_repository.get_agent_workload(
        db,
        agent_id
    )

    return {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "active_ticket_count": count
    }