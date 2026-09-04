from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import Customer, User


def get_customer_by_id(
    db: Session,
    customer_id: int
):
    return db.query(Customer).filter(
        Customer.id == customer_id
    ).first()


def get_customer_by_user_id(
    db: Session,
    user_id: int
):
    return db.query(Customer).filter(
        Customer.user_id == user_id
    ).first()


def get_customers(
    db: Session,
    search: str = None,
    status: str = None,
    page: int = 1,
    limit: int = 5
):
    query = db.query(Customer).join(User)

    # Search
    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                Customer.company.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%")
            )
        )

    # Filter by status
    if status:
        query = query.filter(
            Customer.status == status
        )

    # Pagination
    offset = (page - 1) * limit

    return query.offset(offset).limit(limit).all()

def create_customer(
    db: Session,
    customer: Customer
):
    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def update_customer(
    db: Session,
    customer: Customer
):
    db.commit()
    db.refresh(customer)

    return customer