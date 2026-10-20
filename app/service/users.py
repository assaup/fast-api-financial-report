from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repository import users as user_repository
from app.schemas import UserCreateRequest, UserResponse, LoginRequest, TokenResponse
from app.security import hash_password, verify_password, create_access_token


def create_user(db: Session, payload: UserCreateRequest) -> UserResponse:
    if user_repository.get_user(db, payload.login):
        raise HTTPException(status_code = 400, detail="User already exists")

    user = user_repository.create_user(db, payload.login, hashed_password=hash_password(payload.password))
    db.commit()
    return UserResponse.model_validate(user)

def login(db: Session, payload: LoginRequest) -> TokenResponse:
    user = user_repository.get_user(db, payload.login)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect login or password", headers={"WWW-Authenticate": "Bearer"})
    
    access_token=create_access_token(user.id)
    return TokenResponse(access_token=access_token)