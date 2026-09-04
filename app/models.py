from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


# =========================================================
# USER
# =========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        default="customer",
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    customer = relationship(
        "Customer",
        back_populates="user",
        uselist=False
    )

    tickets = relationship(
        "Ticket",
        back_populates="assigned_user"
    )


# =========================================================
# CUSTOMER
# =========================================================

class Customer(Base):
    __tablename__ = "customers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    phone = Column(
        String(20)
    )

    company = Column(
        String(255)
    )

    address = Column(
        Text
    )

    status = Column(
        String(20),
        default="active",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="customer"
    )

    tickets = relationship(
        "Ticket",
        back_populates="customer"
    )


# =========================================================
# CATEGORY
# =========================================================

class Category(Base):
    __tablename__ = "categories"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        unique=True,
        nullable=False
    )

    description = Column(
        Text
    )

    tickets = relationship(
        "Ticket",
        back_populates="category"
    )


# =========================================================
# TICKET
# =========================================================

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    subject = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        default="open",
        nullable=False
    )

    priority = Column(
        String(50),
        default="medium",
        nullable=False
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id")
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id")
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Added for ticket resolution tracking
    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    customer = relationship(
        "Customer",
        back_populates="tickets"
    )

    category = relationship(
        "Category",
        back_populates="tickets"
    )

    assigned_user = relationship(
        "User",
        back_populates="tickets"
    )


# =========================================================
# TICKET COMMENT
# =========================================================

class TicketComment(Base):
    __tablename__ = "ticket_comments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ticket_id = Column(
        Integer,
        ForeignKey(
            "tickets.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    comment = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    ticket = relationship(
        "Ticket"
    )

    user = relationship(
        "User"
    )


# =========================================================
# TICKET ATTACHMENT
# =========================================================

class TicketAttachment(Base):
    __tablename__ = "ticket_attachments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ticket_id = Column(
        Integer,
        ForeignKey(
            "tickets.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    file_name = Column(
        String,
        nullable=False
    )

    file_path = Column(
        String,
        nullable=False
    )

    file_size = Column(
        Integer,
        nullable=False
    )

    file_type = Column(
        String,
        nullable=False
    )

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    ticket = relationship(
        "Ticket"
    )

    user = relationship(
        "User"
    )


# =========================================================
# NOTIFICATION
# =========================================================

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    title = Column(
        String,
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = relationship(
        "User"
    )


# =========================================================
# SLA TRACKING
# =========================================================

class SLATracking(Base):
    __tablename__ = "sla_tracking"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ticket_id = Column(
        Integer,
        ForeignKey(
            "tickets.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True
    )

    priority = Column(
        String,
        nullable=False
    )

    deadline = Column(
        DateTime,
        nullable=False
    )

    first_response_at = Column(
        DateTime,
        nullable=True
    )

    resolved_at = Column(
        DateTime,
        nullable=True
    )

    resolution_time = Column(
        Integer,
        nullable=True
    )

    status = Column(
        String,
        default="Within SLA",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    ticket = relationship(
        "Ticket"
    )
    
class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    action = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    ticket = relationship("Ticket")
    user = relationship("User")
    
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    entity = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=False)
    previous_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = relationship("User")