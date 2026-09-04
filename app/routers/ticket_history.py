from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import TicketHistoryResponse
from app.services import ticket_history_service


router = APIRouter(
    prefix="/tickets",
    tags=["Ticket History"]
)


@router.get(
    "/{ticket_id}/history",
    response_model=list[TicketHistoryResponse]
)
def get_ticket_history(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ticket_history_service.get_ticket_history(
        db,
        ticket_id,
        current_user
    )