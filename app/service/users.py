from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool

from app.repository import users as user_repository
from app.schemas import UserCreateRequest, UserResponse, LoginRequest, TokenResponse
from app.security import hash_password, verify_password, create_access_token


async def create_user(db: AsyncSession, payload: UserCreateRequest) -> UserResponse:
    if await user_repository.get_user(db, payload.login):
        raise HTTPException(status_code = 400, detail="User already exists")

    hashed = await run_in_threadpool(hash_password, payload.password)
    user = await user_repository.create_user(db, payload.login, hashed_password=hashed)
    await db.commit()
    return UserResponse.model_validate(user)

async def login(db: AsyncSession, payload: LoginRequest) -> TokenResponse:
    user = await user_repository.get_user(db, payload.login)
    hashed = await run_in_threadpool(verify_password, payload.password, user.hashed_password)
    if user is None or not hashed:
        raise HTTPException(status_code=401, detail="Incorrect login or password", headers={"WWW-Authenticate": "Bearer"})
    
    access_token=create_access_token(user.id)
    return TokenResponse(access_token=access_token)