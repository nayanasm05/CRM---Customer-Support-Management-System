from sqlalchemy.orm import Session

from app.models import AuditLog


def create_audit_log(
    db: Session,
    user_id: int,
    action: str,
    entity: str,
    entity_id: int,
    previous_value: str = None,
    new_value: str = None
):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        previous_value=previous_value,
        new_value=new_value
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


def get_audit_logs(db: Session):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .all()
    )


def get_audit_log_by_id(db: Session, audit_id: int):
    return (
        db.query(AuditLog)
        .filter(AuditLog.id == audit_id)
        .first()
    )