from sqlalchemy.orm import Session
from typing import Generator
from app.database import SessionLocal
from fastapi import Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models import User
from app.repository import users as users_repository

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                     db: Session = Depends(get_db)) -> User:
    login = credentials.credentials

    user = users_repository.get_user(db, login)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

class Pagination:
    def __init__(
            self,
            limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0),
    ):
        self.limit = limit
        self.offset = offset