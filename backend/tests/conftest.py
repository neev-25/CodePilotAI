"""
Shared fixtures for all backend tests.
Uses an in-memory SQLite database so tests never touch the real data file.
"""
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.database.database import Base
from main import app

# ── In-memory SQLite engine ─────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once per test session."""
    # Import all models so Base.metadata knows about them
    import app.models.user            # noqa: F401
    import app.models.repository      # noqa: F401
    import app.models.indexing_job    # noqa: F401
    import app.models.analysis_cache  # noqa: F401

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """Yield a transactional DB session, rolled back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    """
    TestClient with get_db overridden to use the test session.
    Also overrides the Celery task to a no-op so indexing tests don't dispatch.
    """
    from app.api.auth import get_db as auth_get_db
    from app.api.repository import get_db as repo_get_db

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[auth_get_db] = _override_get_db
    app.dependency_overrides[repo_get_db] = _override_get_db

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    """Register a test user and return Bearer auth headers."""
    client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@codepilot.dev",
        "password": "testpassword123",
    })
    resp = client.post("/auth/login", json={
        "email": "test@codepilot.dev",
        "password": "testpassword123",
    })
    token = resp.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}
