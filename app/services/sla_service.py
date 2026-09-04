from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import SLATracking, Ticket


SLA_HOURS = {
    "low": 48,
    "medium": 24,
    "high": 8,
    "critical": 2
}


def calculate_sla_deadline(
    priority: str,
    created_at: datetime | None = None
):
    if created_at is None:
        created_at = datetime.utcnow()

    hours = SLA_HOURS.get(
        priority.lower(),
        24
    )

    return created_at + timedelta(hours=hours)


def is_sla_breached(
    priority: str,
    created_at: datetime,
    current_time: datetime | None = None
):
    if current_time is None:
        current_time = datetime.utcnow()

    deadline = calculate_sla_deadline(
        priority,
        created_at
    )

    return current_time > deadline


def create_sla_tracking(
    db: Session,
    ticket: Ticket
):
    deadline = calculate_sla_deadline(
        ticket.priority,
        ticket.created_at
    )

    sla = SLATracking(
        ticket_id=ticket.id,
        priority=ticket.priority,
        deadline=deadline,
        status="Within SLA"
    )

    db.add(sla)
    db.commit()
    db.refresh(sla)

    return sla


def get_sla_status(
    sla: SLATracking
):
    current_time = datetime.utcnow()

    if sla.resolved_at:
        if sla.resolved_at <= sla.deadline:
            return "Within SLA"

        return "Breached"

    if current_time > sla.deadline:
        return "Breached"

    remaining_time = sla.deadline - current_time

    # At Risk when less than 1 hour remains
    if remaining_time.total_seconds() <= 3600:
        return "At Risk"

    return "Within SLA"


def update_sla_status(
    db: Session,
    sla: SLATracking
):
    sla.status = get_sla_status(sla)

    db.commit()
    db.refresh(sla)

    return sla


def get_all_sla(
    db: Session
):
    sla_records = db.query(
        SLATracking
    ).all()

    for sla in sla_records:
        sla.status = get_sla_status(sla)

    db.commit()

    return sla_records


def get_breached_sla(
    db: Session
):
    sla_records = db.query(
        SLATracking
    ).all()

    breached = []

    for sla in sla_records:
        if get_sla_status(sla) == "Breached":
            breached.append(sla)

    return breached


def get_at_risk_sla(
    db: Session
):
    sla_records = db.query(
        SLATracking
    ).all()

    at_risk = []

    for sla in sla_records:
        if get_sla_status(sla) == "At Risk":
            at_risk.append(sla)

    return at_risk


# =========================
# BACKGROUND SLA MONITORING
# =========================

def monitor_sla():
    from app.database import SessionLocal

    db = SessionLocal()

    try:
        sla_records = db.query(SLATracking).all()

        updated_count = 0

        for sla in sla_records:
            new_status = get_sla_status(sla)

            if sla.status != new_status:
                sla.status = new_status
                updated_count += 1

        db.commit()

        return {
            "message": "SLA monitoring completed",
            "updated_count": updated_count,
            "checked_count": len(sla_records)
        }

    finally:
        db.close()