from sqlalchemy.orm import Session

from app.models import TicketAttachment


def create_attachment(
    db: Session,
    attachment: TicketAttachment
):
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return attachment


def get_attachments_by_ticket(
    db: Session,
    ticket_id: int
):
    return db.query(TicketAttachment).filter(
        TicketAttachment.ticket_id == ticket_id
    ).all()


def get_attachment_by_id(
    db: Session,
    attachment_id: int
):
    return db.query(TicketAttachment).filter(
        TicketAttachment.id == attachment_id
    ).first()


def delete_attachment(
    db: Session,
    attachment: TicketAttachment
):
    db.delete(attachment)
    db.commit()