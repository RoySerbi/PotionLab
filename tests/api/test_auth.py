from datetime import timedelta
from typing import Any

from fastapi.testclient import TestClient
from jose import jwt
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.models import User


def test_register_user_returns_201(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "bartender", "password": "shaken-not-stirred"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "bartender"
    assert data["role"] == "reader"
    assert "id" in data


def test_register_duplicate_user_returns_409(client: TestClient) -> None:
    first = client.post(
        "/api/v1/auth/register",
        json={"username": "dup-user", "password": "secret123"},
    )
    assert first.status_code == 201

    second = client.post(
        "/api/v1/auth/register",
        json={"username": "dup-user", "password": "secret123"},
    )
    assert second.status_code == 409


def test_register_stores_hashed_password(client: TestClient, session: Session) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "hash-user", "password": "my-password"},
    )
    assert response.status_code == 201

    user = session.exec(select(User).where(User.username == "hash-user")).first()
    assert user is not None
    assert user.hashed_password != "my-password"
    assert "$2" in user.hashed_password


def test_login_valid_credentials_returns_jwt(client: TestClient) -> None:
    created = client.post(
        "/api/v1/auth/register",
        json={"username": "login-user", "password": "secret123"},
    )
    assert created.status_code == 201

    response = client.post(
        "/api/v1/auth/token",
        json={"username": "login-user", "password": "secret123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    payload = jwt.decode(
        data["access_token"],
        settings.jwt_secret or "",
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == "login-user"
    assert payload["role"] == "reader"


def test_login_wrong_password_returns_401(client: TestClient) -> None:
    created = client.post(
        "/api/v1/auth/register",
        json={"username": "wrong-pass", "password": "secret123"},
    )
    assert created.status_code == 201

    response = client.post(
        "/api/v1/auth/token",
        json={"username": "wrong-pass", "password": "bad-pass"},
    )
    assert response.status_code == 401


def test_login_missing_user_returns_401(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/token",
        json={"username": "missing-user", "password": "secret123"},
    )
    assert response.status_code == 401


def test_missing_user_login_triggers_dummy_hash(
    session: Session, monkeypatch: Any
) -> None:
    calls: list[str] = []
    original_hash = security.pwd_context.hash

    def tracking_hash(
        secret: str | bytes,
        scheme: str | None = None,
        category: str | None = None,
        **kwargs: Any,
    ) -> str:
        calls.append(secret.decode() if isinstance(secret, bytes) else secret)
        return original_hash(
            secret,
            scheme=scheme,
            category=category,
            **kwargs,
        )

    monkeypatch.setattr(security.pwd_context, "hash", tracking_hash)
    user = security.authenticate_user(session, "absent-user", "secret123")

    assert user is None
    assert "dummy" in calls


def test_mutation_endpoint_without_token_returns_401(
    client: TestClient,
) -> None:
    """POST/PUT/DELETE require auth, but GET does not per Task 27."""
    response = client.post(
        "/api/v1/cocktails/",
        json={
            "name": "Test",
            "difficulty": 1,
            "instructions": "Test",
            "ingredients": [],
        },
    )
    assert response.status_code == 401


def test_mutation_endpoint_with_invalid_token_returns_401(
    client: TestClient,
) -> None:
    """POST/PUT/DELETE require valid auth, but GET does not per Task 27."""
    response = client.post(
        "/api/v1/cocktails/",
        json={
            "name": "Test",
            "difficulty": 1,
            "instructions": "Test",
            "ingredients": [],
        },
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


def test_get_endpoint_public_access(client: TestClient) -> None:
    """GET endpoints are public per Task 27."""
    response = client.get("/api/v1/cocktails/")
    assert response.status_code == 200


def test_me_endpoint_returns_payload(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "reader-user"
    assert data["role"] == "reader"


def test_expired_token_rejected_on_mutation(client: TestClient) -> None:
    """Expired tokens should be rejected on mutation endpoints."""
    expired_token = create_access_token(
        {"sub": "expired", "role": "editor"},
        expires_delta=timedelta(minutes=-1),
    )
    response = client.post(
        "/api/v1/cocktails/",
        json={
            "name": "Test",
            "difficulty": 1,
            "instructions": "Test",
            "ingredients": [],
        },
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401


def test_role_based_access_admin_can_delete(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    created = client.post(
        "/api/v1/auth/register",
        json={"username": "delete-me", "password": "delete123"},
    )
    assert created.status_code == 201

    response = client.delete("/api/v1/auth/users/delete-me", headers=admin_headers)
    assert response.status_code == 204


def test_role_based_access_reader_cannot_delete(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    created = client.post(
        "/api/v1/auth/register",
        json={"username": "cannot-delete", "password": "delete123"},
    )
    assert created.status_code == 201

    response = client.delete("/api/v1/auth/users/cannot-delete", headers=auth_headers)
    assert response.status_code == 403


def test_role_claim_embedded_in_admin_token(
    client: TestClient, session: Session
) -> None:
    user = User(
        username="admin-claim",
        hashed_password=hash_password("admin1234"),
        role="admin",
    )
    session.add(user)
    session.commit()

    login = client.post(
        "/api/v1/auth/token",
        json={"username": "admin-claim", "password": "admin1234"},
    )
    assert login.status_code == 200

    token = login.json()["access_token"]
    payload = jwt.decode(
        token,
        settings.jwt_secret or "",
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["role"] == "admin"


def test_admin_jwt_contains_admin_role(client: TestClient, session: Session) -> None:
    """Verify admin user gets admin role in JWT token."""
    from jose import jwt

    from app.core.config import settings

    # Create admin user
    admin = User(
        username="test_admin",
        hashed_password=hash_password("admin123"),
        role="admin",
    )
    session.add(admin)
    session.commit()

    # Login
    response = client.post(
        "/api/v1/auth/token",
        json={"username": "test_admin", "password": "admin123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Decode token and verify role
    payload = jwt.decode(
        token, settings.jwt_secret or "", algorithms=[settings.jwt_algorithm]
    )
    assert payload["role"] == "admin", (
        f"Expected role='admin', got role='{payload['role']}'"
    )
    assert payload["sub"] == "test_admin"
