from sqlalchemy.orm import Session

from app.models import Category


def get_category_by_id(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str):
    return db.query(Category).filter(Category.name == name).first()


def get_categories(db: Session):
    return db.query(Category).all()


def create_category(db: Session, category: Category):
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category: Category):
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category):
    db.delete(category)
    db.commit()