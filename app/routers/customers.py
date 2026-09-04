from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User, Customer
from app.repositories import customer_repository
from app.schemas import CustomerCreate, CustomerResponse
from app.services import audit_service

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.post("/", response_model=CustomerResponse)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "customer"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    if current_user.role == "customer":
        user_id = current_user.id
    else:
        raise HTTPException(
            status_code=400,
            detail="Admin customer creation requires a user ID"
        )

    existing_customer = db.query(Customer).filter(
        Customer.user_id == user_id
    ).first()

    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="Customer profile already exists"
        )

    customer = Customer(
        user_id=user_id,
        phone=customer_data.phone,
        company=customer_data.company,
        address=customer_data.address,
        status=customer_data.status or "active"
    )

    customer = customer_repository.create_customer(
        db,
        customer
    )

    return CustomerResponse(
        id=customer.id,
        name=customer.user.name,
        email=customer.user.email,
        phone=customer.phone,
        company=customer.company,
        address=customer.address,
        status=customer.status,
        created_at=customer.created_at
    )


@router.get("/", response_model=list[CustomerResponse])
def get_all_customers(
    search: str = None,
    status: str = None,
    page: int = 1,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )

    customers = customer_repository.get_customers(
        db,
        search,
        status,
        page,
        limit
    )

    result = []

    for customer in customers:
        result.append(
            CustomerResponse(
                id=customer.id,
                name=customer.user.name,
                email=customer.user.email,
                phone=customer.phone,
                company=customer.company,
                address=customer.address,
                status=customer.status,
                created_at=customer.created_at
            )
        )

    return result


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = customer_repository.get_customer_by_id(
        db,
        customer_id
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return CustomerResponse(
        id=customer.id,
        name=customer.user.name,
        email=customer.user.email,
        phone=customer.phone,
        company=customer.company,
        address=customer.address,
        status=customer.status,
        created_at=customer.created_at
    )


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = customer_repository.get_customer_by_id(
        db,
        customer_id
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    # Store old values for audit log
    old_phone = customer.phone
    old_company = customer.company
    old_address = customer.address
    old_status = customer.status

    customer.phone = customer_data.phone
    customer.company = customer_data.company
    customer.address = customer_data.address

    if customer_data.status:
        customer.status = customer_data.status

    db.commit()
    db.refresh(customer)

    # Create audit log
    audit_service.create_audit_log(
        db,
        current_user.id,
        "customer_updated",
        "customer",
        customer.id,
        (
            f"phone={old_phone}, "
            f"company={old_company}, "
            f"address={old_address}, "
            f"status={old_status}"
        ),
        (
            f"phone={customer.phone}, "
            f"company={customer.company}, "
            f"address={customer.address}, "
            f"status={customer.status}"
        )
    )

    return CustomerResponse(
        id=customer.id,
        name=customer.user.name,
        email=customer.user.email,
        phone=customer.phone,
        company=customer.company,
        address=customer.address,
        status=customer.status,
        created_at=customer.created_at
    )


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    customer = customer_repository.get_customer_by_id(
        db,
        customer_id
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    db.delete(customer)
    db.commit()

    return {
        "message": "Customer deleted successfully"
    }


@router.get("/{customer_id}/tickets")
def get_customer_tickets(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = customer_repository.get_customer_by_id(
        db,
        customer_id
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer.tickets