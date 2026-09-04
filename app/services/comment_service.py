from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Ticket, TicketComment
from app.repositories import comment_repository
from app.services import notification_service
from app.services import audit_service

def check_ticket_access(
    db: Session,
    ticket_id: int,
    current_user
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Admin can access any ticket
    if current_user.role == "admin":
        return ticket

    # Support agent can access only tickets assigned to them
    if current_user.role == "support_agent":
        if ticket.assigned_to != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to access this ticket"
            )

        return ticket

    # Customer can access only their own tickets
    if current_user.role == "customer":
        if ticket.customer.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to access this ticket"
            )

        return ticket

    raise HTTPException(
        status_code=403,
        detail="Access denied"
    )



def create_comment(
    db: Session,
    ticket_id: int,
    comment_data,
    current_user
):
    ticket = check_ticket_access(
        db,
        ticket_id,
        current_user
    )

    # Closed tickets cannot receive comments
    if ticket.status == "closed":
        raise HTTPException(
            status_code=400,
            detail="Closed tickets cannot accept new comments"
        )

    # Cancelled tickets cannot receive comments
    if ticket.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Cancelled tickets cannot accept new comments"
        )

    # Check whether this is the first support-agent response
    from app.models import SLATracking

    sla_tracking = db.query(SLATracking).filter(
        SLATracking.ticket_id == ticket_id
    ).first()

    is_first_response = (
        current_user.role == "support_agent"
        and sla_tracking is not None
        and sla_tracking.first_response_at is None
    )

    comment = TicketComment(
        ticket_id=ticket_id,
        user_id=current_user.id,
        comment=comment_data.comment
    )

    comment = comment_repository.create_comment(
        db,
        comment
    )

    # Record first support-agent response for SLA
    if is_first_response:
        from datetime import datetime, timezone

        sla_tracking.first_response_at = datetime.now(timezone.utc).replace(
            tzinfo=None
        )

        db.commit()
        db.refresh(sla_tracking)

    # Notify customer
    if ticket.customer:
        notification_service.create_notification(
            db,
            ticket.customer.user_id,
            "New Comment",
            f"A new comment was added to ticket #{ticket.id}."
        )

    # Notify assigned support agent
    if (
        ticket.assigned_to
        and ticket.assigned_to != current_user.id
    ):
        notification_service.create_notification(
            db,
            ticket.assigned_to,
            "New Comment",
            f"A new comment was added to ticket #{ticket.id}."
        )

    return comment



def get_ticket_comments(
    db: Session,
    ticket_id: int,
    current_user
):
    check_ticket_access(
        db,
        ticket_id,
        current_user
    )

    return comment_repository.get_comments_by_ticket(
        db,
        ticket_id
    )


def update_comment(
    db: Session,
    comment_id: int,
    comment_data,
    current_user
):
    comment = comment_repository.get_comment_by_id(
        db,
        comment_id
    )

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    # Check access to the ticket
    ticket = check_ticket_access(
        db,
        comment.ticket_id,
        current_user
    )

    if ticket.status == "closed":
        raise HTTPException(
            status_code=400,
            detail="Closed tickets cannot be modified"
        )

    # Customer cannot modify support-agent comments
    if (
        current_user.role == "customer"
        and comment.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Customers cannot modify comments created by support agents"
        )

    # Users can modify their own comments
    # Admin can modify any comment
    if (
        current_user.role != "admin"
        and comment.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only modify your own comments"
        )

    comment.comment = comment_data.comment

    return comment_repository.update_comment(
        db,
        comment
    )


def delete_comment(
    db: Session,
    comment_id: int,
    current_user
):
    comment = comment_repository.get_comment_by_id(
        db,
        comment_id
    )

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    ticket = check_ticket_access(
        db,
        comment.ticket_id,
        current_user
    )

    if ticket.status == "closed":
        raise HTTPException(
            status_code=400,
            detail="Closed tickets cannot be modified"
        )

    # Only comment owner or admin can delete
    if (
        current_user.role != "admin"
        and comment.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own comments"
        )

    # Store comment details before deletion
    comment_text = comment.comment
    ticket_id = comment.ticket_id

    comment_repository.delete_comment(
        db,
        comment
    )

    # Create audit log
    audit_service.create_audit_log(
        db,
        current_user.id,
        "comment_deleted",
        "ticket_comment",
        comment_id,
        f"ticket_id={ticket_id}, comment={comment_text}",
        None
    )

    return {
        "message": "Comment deleted successfully"
    }