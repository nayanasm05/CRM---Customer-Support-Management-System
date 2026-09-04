from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# =========================================================
# AUTH / USER SCHEMAS
# =========================================================

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "customer"


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# =========================================================
# CUSTOMER SCHEMAS
# =========================================================

class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = "active"

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        
# =========================================================
# TICKET SCHEMAS
# =========================================================

class TicketCreate(BaseModel):
    subject: str
    description: str
    priority: Optional[str] = "medium"
    category_id: Optional[int] = None


class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None


class TicketReassign(BaseModel):
    assigned_to: int


class TicketResponse(BaseModel):
    id: int
    subject: str
    description: str
    status: str
    priority: str
    customer_id: int
    category_id: Optional[int] = None
    assigned_to: Optional[int] = None

    class Config:
        from_attributes = True

class TicketHistoryResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    action: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True
        
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
        
        
class CommentCreate(BaseModel):
    comment: str


class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    comment: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
class AttachmentResponse(BaseModel):
    id: int
    ticket_id: int
    uploaded_by: int
    file_name: str
    file_path: str
    file_size: int
    file_type: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
        
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
        
class SLAResponse(BaseModel):
    id: int
    ticket_id: int
    priority: str
    deadline: datetime
    first_response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_time: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        
class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    entity: str
    entity_id: int
    previous_value: str | None = None
    new_value: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True