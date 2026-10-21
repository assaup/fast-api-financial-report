from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from sqlalchemy import select

async def get_user(db: AsyncSession, login:str) -> User | None:
    stmt = select(User).where(User.login == login)
    return await db.scalar(stmt)

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def create_user(db: AsyncSession, login: str, hashed_password: str) -> User:
    user = User(login=login, hashed_password=hashed_password)
    db.add(user)
    await db.flush()
    return user

