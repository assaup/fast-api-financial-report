from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from app.database import AsyncSessionLocal
from fastapi import Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models import User
from app.repository import users as users_repository
from app.security import decode_access_token

security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> User:
    unauthorized = HTTPException(
        status_code=401,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise unauthorized

    user = await users_repository.get_user_by_id(db, user_id)

    if not user:
        raise unauthorized
    return user


class Pagination:
    def __init__(
            self,
            limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0),
    ):
        self.limit = limit
        self.offset = offset