from sqlalchemy.orm import Session

from app.models import AuditLog


def get_all_audit_logs(db: Session):
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