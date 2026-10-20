from fastapi import APIRouter, Depends, status
from app.schemas import UserCreateRequest, UserResponse, TokenResponse, LoginRequest
from app.service import users as users_service
from sqlalchemy.orm import Session
from app.dependency import get_db, get_current_user
from app.models import User

router = APIRouter()

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreateRequest, db: Session = Depends(get_db)):
    return users_service.create_user(db, payload)

@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return users_service.login(db, payload)

@router.get("/user/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)