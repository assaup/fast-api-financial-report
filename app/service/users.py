from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.repository import users as user_repository
from app.schemas import LoginRequest, TokenResponse, UserCreateRequest, UserResponse
from app.security import create_access_token, hash_password, verify_password


async def create_user(db: AsyncSession, payload: UserCreateRequest) -> UserResponse:
    if await user_repository.get_user(db, payload.login):
        raise UserAlreadyExistsError(payload.login)

    hashed = await run_in_threadpool(hash_password, payload.password)
    user = await user_repository.create_user(db, payload.login, hashed_password=hashed)
    await db.commit()
    return UserResponse.model_validate(user)


async def login(db: AsyncSession, payload: LoginRequest) -> TokenResponse:
    user = await user_repository.get_user(db, payload.login)
    if user is None or not await run_in_threadpool(verify_password, payload.password, user.hashed_password):
        raise InvalidCredentialsError()

    access_token = create_access_token(user.id)
    return TokenResponse(access_token=access_token)
