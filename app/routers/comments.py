from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import CommentCreate, CommentResponse
from app.services import comment_service


router = APIRouter(
    tags=["Comments"]
)


@router.post(
    "/tickets/{ticket_id}/comments",
    response_model=CommentResponse
)
def add_comment(
    ticket_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return comment_service.create_comment(
        db,
        ticket_id,
        comment_data,
        current_user
    )


@router.get(
    "/tickets/{ticket_id}/comments",
    response_model=list[CommentResponse]
)
def get_ticket_comments(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return comment_service.get_ticket_comments(
        db,
        ticket_id,
        current_user
    )


@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse
)
def update_comment(
    comment_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return comment_service.update_comment(
        db,
        comment_id,
        comment_data,
        current_user
    )


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return comment_service.delete_comment(
        db,
        comment_id,
        current_user
    )