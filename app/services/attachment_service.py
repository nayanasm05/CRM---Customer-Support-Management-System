import os
import uuid

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models import Ticket, TicketAttachment
from app.repositories import attachment_repository


UPLOAD_DIR = "uploads"

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".doc",
    ".docx",
    ".txt"
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


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

    if current_user.role == "admin":
        return ticket

    if current_user.role == "support_agent":
        if ticket.assigned_to != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to access this ticket"
            )

        return ticket

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


async def create_attachment(
    db: Session,
    ticket_id: int,
    file: UploadFile,
    current_user
):
    ticket = check_ticket_access(
        db,
        ticket_id,
        current_user
    )

    if ticket.status in ["closed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail="Attachments cannot be added to closed or cancelled tickets"
        )

    original_filename = file.filename or ""

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="File type not allowed"
        )

    file_content = await file.read()

    file_size = len(file_content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size must not exceed 5 MB"
        )

    os.makedirs(
        UPLOAD_DIR,
        exist_ok=True
    )

    unique_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        unique_filename
    )

    with open(file_path, "wb") as buffer:
        buffer.write(file_content)

    attachment = TicketAttachment(
        ticket_id=ticket_id,
        uploaded_by=current_user.id,
        file_name=original_filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file.content_type or extension,
    )

    return attachment_repository.create_attachment(
        db,
        attachment
    )


def get_ticket_attachments(
    db: Session,
    ticket_id: int,
    current_user
):
    check_ticket_access(
        db,
        ticket_id,
        current_user
    )

    return attachment_repository.get_attachments_by_ticket(
        db,
        ticket_id
    )


def get_attachment(
    db: Session,
    attachment_id: int,
    current_user
):
    attachment = attachment_repository.get_attachment_by_id(
        db,
        attachment_id
    )

    if not attachment:
        raise HTTPException(
            status_code=404,
            detail="Attachment not found"
        )

    check_ticket_access(
        db,
        attachment.ticket_id,
        current_user
    )

    return attachment


def delete_attachment(
    db: Session,
    attachment_id: int,
    current_user
):
    attachment = attachment_repository.get_attachment_by_id(
        db,
        attachment_id
    )

    if not attachment:
        raise HTTPException(
            status_code=404,
            detail="Attachment not found"
        )

    check_ticket_access(
        db,
        attachment.ticket_id,
        current_user
    )

    if (
        current_user.role != "admin"
        and attachment.uploaded_by != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own attachments"
        )

    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)

    attachment_repository.delete_attachment(
        db,
        attachment
    )

    return {
        "message": "Attachment deleted successfully"
    }