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
from app.database import Base

TEST_DATABASE_URL = "sqlite:///./test.db"

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
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def task_factory(db_session):
    def _create_task(**kwargs):
        return create_task(db_session, **kwargs)
    return _create_task

TEST_DB_PATH = "test.db"

@pytest.fixture(scope="session", autouse=True)
def clean_up_test_db():
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)