from fastapi.testclient import TestClient
from sqlmodel import Session
from app.core.security import hash_password
from app.models import User
from app.core.config import settings
from jose import jwt
from app.main import app
from app.db.session import get_session

def test_admin_jwt_contains_admin_role(client: TestClient, session: Session) -> None:
    admin = User(
        username="test_admin",
        hashed_password=hash_password("admin123"),
        role="admin",
    )
    session.add(admin)
    session.commit()
    
    # Using /api/v1/auth/token since that's what exists
    response = client.post(
        "/api/v1/auth/token",
        json={"username": "test_admin", "password": "admin123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    print(f"Payload role: {payload.get('role')}")
    assert payload["role"] == "admin", f"Expected role='admin', got role='{payload['role']}'"

import pytest
from tests.conftest import client_fixture, session_fixture

# Run it manually via pytest
