import os
import pytest
from alembic import command
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from fastapi.testclient import TestClient

from .factories.task_factory import create_task
from app.main import app
from app.database import get_db

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

ALEMBIC_CFG = Config(os.path.join(BASE_DIR, "alembic.ini"))
ALEMBIC_CFG.set_main_option("script_location", os.path.join(BASE_DIR, "alembic"))
ALEMBIC_CFG.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def reset_database():
    if TEST_DATABASE_URL.startswith("sqlite:///./") and os.path.exists("test.db"):
        os.remove("test.db")
    command.upgrade(ALEMBIC_CFG, "head")
    yield

@pytest.fixture
def task_factory(db_session):
    def _create_task(**kwargs):
        return create_task(db_session, **kwargs)
    return _create_task