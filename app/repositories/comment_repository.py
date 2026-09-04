from sqlalchemy.orm import Session

from app.models import TicketComment


def create_comment(
    db: Session,
    comment: TicketComment
):
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


def get_comments_by_ticket(
    db: Session,
    ticket_id: int
):
    return db.query(TicketComment).filter(
        TicketComment.ticket_id == ticket_id
    ).order_by(
        TicketComment.created_at.asc()
    ).all()


def get_comment_by_id(
    db: Session,
    comment_id: int
):
    return db.query(TicketComment).filter(
        TicketComment.id == comment_id
    ).first()


def update_comment(
    db: Session,
    comment: TicketComment
):
    db.commit()
    db.refresh(comment)

    return comment


def delete_comment(
    db: Session,
    comment: TicketComment
):
    db.delete(comment)
    db.commit()