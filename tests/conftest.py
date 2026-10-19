import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from main import app
from app.dependency import get_db
from fastapi.testclient import TestClient
from app.database import Base

DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def get_test_db() -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = get_test_db


@pytest.fixture()
def client():
    yield TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture()
def db_session()-> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()