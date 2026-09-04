from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Category
from app.repositories import category_repository


def create_category(
    db: Session,
    category_data
):
    existing = category_repository.get_category_by_name(
        db,
        category_data.name
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    category = Category(
        name=category_data.name,
        description=category_data.description
    )

    return category_repository.create_category(
        db,
        category
    )


def get_categories(db: Session):
    return category_repository.get_categories(db)


def get_category_by_id(
    db: Session,
    category_id: int
):
    category = category_repository.get_category_by_id(
        db,
        category_id
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


def update_category(
    db: Session,
    category_id: int,
    category_data
):
    category = category_repository.get_category_by_id(
        db,
        category_id
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    category.name = category_data.name
    category.description = category_data.description

    return category_repository.update_category(
        db,
        category
    )


def delete_category(
    db: Session,
    category_id: int
):
    category = category_repository.get_category_by_id(
        db,
        category_id
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    category_repository.delete_category(
        db,
        category
    )

    return {
        "message": "Category deleted successfully"
    }