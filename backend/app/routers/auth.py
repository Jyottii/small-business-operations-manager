from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.schemas.user import UserResponse
from app.schemas.base import ResponseModel
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(
    data: UserRegister,
    response: Response,
    db: Session = Depends(get_db)
):
    try:
        user, token = AuthService.register_user(db, data)
        db.commit()
        db.refresh(user)

        # Set secure HttpOnly cookie
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            samesite="lax",
            secure=False  # Allow local dev over http, set to True in HTTPS prod
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user
        }
    except Exception as e:
        db.rollback()
        raise e

@router.post("/login", response_model=TokenResponse)
def login(
    data: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    try:
        user, token = AuthService.authenticate_user(db, data)
        db.commit()

        # Set secure HttpOnly cookie
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            samesite="lax",
            secure=False
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user
        }
    except Exception as e:
        db.rollback()
        raise e

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
