from fastapi import APIRouter, Depends, status
from app.schemas import UserCreateRequest, UserResponse, TokenResponse, LoginRequest
from app.service import users as users_service
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependency import get_db, get_current_user
from app.models import User
from app.api.responses import error_responses, AUTH_ERRORS
from app.exceptions import UserAlreadyExistsError, InvalidCredentialsError  

router = APIRouter()

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, responses=error_responses(UserAlreadyExistsError("samir")))
async def create_user(payload: UserCreateRequest, db: AsyncSession = Depends(get_db)):
    return await users_service.create_user(db, payload)

@router.post("/auth/login", response_model=TokenResponse, responses=error_responses(InvalidCredentialsError()))
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await users_service.login(db, payload)

@router.get("/user/me", response_model=UserResponse, responses=error_responses(*AUTH_ERRORS, validation=False))
def read_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)