from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import register_user, login_user
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    return register_user(db, user_data)


@router.post("/login", response_model=Token)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    return login_user(db, user_data)

@router.get("/profile")
def get_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }


@router.put("/profile")
def update_profile(
    name: str,
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.name = name
    current_user.email = email

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully",
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }


@router.put("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(old_password, current_user.password):
        raise HTTPException(
            status_code=400,
            detail="Old password is incorrect"
        )

    current_user.password = hash_password(new_password)

    db.commit()

    return {
        "message": "Password changed successfully"
    }