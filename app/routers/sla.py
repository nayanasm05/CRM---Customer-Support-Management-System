from fastapi import APIRouter, BackgroundTasks, Depends

from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import SLAResponse
from app.services import sla_service


router = APIRouter(
    prefix="/sla",
    tags=["SLA"]
)


# =========================
# GET ALL SLA RECORDS
# =========================

@router.get("/tickets", response_model=list[SLAResponse])
def get_sla_tickets(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    background_tasks.add_task(
        sla_service.monitor_sla
    )

    return sla_service.get_all_sla(db)
# =========================
# GET BREACHED SLA
# =========================

@router.get(
    "/breached",
    response_model=list[SLAResponse]
)
def get_breached_sla(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return sla_service.get_breached_sla(db)


# =========================
# GET AT-RISK SLA
# =========================

@router.get(
    "/at-risk",
    response_model=list[SLAResponse]
)
def get_at_risk_sla(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return sla_service.get_at_risk_sla(db)

