import os

os.environ.setdefault("POTION_JWT_SECRET", "test-jwt-secret")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.security import hash_password
from app.db.session import get_session
from app.main import app
from app.models import User


@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory SQLite session for tests using StaticPool."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with overridden get_session dependency."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient) -> dict[str, str]:
    register_response = client.post(
        "/api/v1/auth/register",
        json={"username": "reader-user", "password": "test1234"},
    )
    assert register_response.status_code == 201

    token_response = client.post(
        "/api/v1/auth/token",
        json={"username": "reader-user", "password": "test1234"},
    )
    assert token_response.status_code == 200

    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="editor_headers")
def editor_headers_fixture(client: TestClient, session: Session) -> dict[str, str]:
    editor = User(
        username="editor-user",
        hashed_password=hash_password("editor1234"),
        role="editor",
    )
    session.add(editor)
    session.commit()

    token_response = client.post(
        "/api/v1/auth/token",
        json={"username": "editor-user", "password": "editor1234"},
    )
    assert token_response.status_code == 200

    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="admin_headers")
def admin_headers_fixture(client: TestClient, session: Session) -> dict[str, str]:
    admin = User(
        username="admin-user",
        hashed_password=hash_password("admin1234"),
        role="admin",
    )
    session.add(admin)
    session.commit()

    token_response = client.post(
        "/api/v1/auth/token",
        json={"username": "admin-user", "password": "admin1234"},
    )
    assert token_response.status_code == 200

    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
