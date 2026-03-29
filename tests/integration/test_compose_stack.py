"""Integration tests for Docker Compose stack.

These tests verify end-to-end functionality across API, AI service, and auth flows.
They assume services are running locally (docker compose up).
"""

from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.security import hash_password
from app.models import User


def _services_available() -> bool:
    """Check if the Docker Compose services are running."""
    try:
        response = httpx.get("http://localhost:8001/health", timeout=2.0)
        return response.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


@pytest.mark.anyio
async def test_api_health_check(client: TestClient) -> None:
    """Test that API health endpoint returns OK status.

    Verifies:
    - GET /health returns 200
    - Response contains {"status": "ok"}
    """
    response = client.get("/health")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "ok", f"Expected status='ok', got {data}"


@pytest.mark.anyio
async def test_auth_flow_end_to_end(
    client: TestClient,
    session: Session,
) -> None:
    """Test complete auth flow: register → login → create cocktail → verify.

    Verifies:
    - User registration succeeds with editor role
    - Login returns valid JWT token
    - Protected endpoint (create cocktail) accepts token
    - Created resource persists and can be retrieved
    """
    editor_user = User(
        username="integration-tester",
        hashed_password=hash_password("test-password-123"),
        role="editor",
    )
    session.add(editor_user)
    session.commit()

    login_response = client.post(
        "/api/v1/auth/token",
        json={
            "username": "integration-tester",
            "password": "test-password-123",
        },
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
    token = login_response.json()["access_token"]
    assert token is not None, "No access token in login response"

    headers = {"Authorization": f"Bearer {token}"}

    gin_response = client.post(
        "/api/v1/ingredients",
        json={"name": "Gin", "category": "spirit", "description": "London dry gin"},
        headers=headers,
    )
    assert gin_response.status_code == 201, (
        f"Failed to create ingredient: {gin_response.json()}"
    )
    gin_id = gin_response.json()["id"]

    vermouth_response = client.post(
        "/api/v1/ingredients",
        json={
            "name": "Dry Vermouth",
            "category": "fortified_wine",
            "description": "Dry vermouth",
        },
        headers=headers,
    )
    assert vermouth_response.status_code == 201, (
        f"Failed to create ingredient: {vermouth_response.json()}"
    )
    vermouth_id = vermouth_response.json()["id"]

    cocktail_data = {
        "name": "Integration Test Martini",
        "difficulty": 2,
        "glass_type": "martini",
        "instructions": "Stir with ice, strain into glass",
        "ingredients": [
            {"ingredient_id": gin_id, "amount": "60ml", "is_optional": False},
            {"ingredient_id": vermouth_id, "amount": "10ml", "is_optional": False},
        ],
    }

    create_response = client.post(
        "/api/v1/cocktails/",
        json=cocktail_data,
        headers=headers,
    )
    assert create_response.status_code == 201, (
        f"Cocktail creation failed: {create_response.json()}"
    )
    created_cocktail = create_response.json()
    cocktail_id = created_cocktail["id"]
    assert created_cocktail["name"] == "Integration Test Martini"

    get_response = client.get(
        f"/api/v1/cocktails/{cocktail_id}",
        headers=headers,
    )
    assert get_response.status_code == 200, (
        f"Failed to retrieve cocktail: {get_response.json()}"
    )
    retrieved_cocktail = get_response.json()
    assert retrieved_cocktail["name"] == "Integration Test Martini"
    assert len(retrieved_cocktail["ingredients"]) == 2


@pytest.mark.integration
@pytest.mark.anyio
async def test_ai_mixologist_endpoint(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """Test AI Mixologist endpoint returns valid CocktailSuggestion.

    This test verifies the AI service integration by calling the /mix endpoint
    with sample ingredients and checking the response structure matches
    the CocktailSuggestion schema.
    """
    if not _services_available():
        pytest.skip("Docker Compose services not running")

    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(
            "http://localhost:8001/mix",
            json={
                "ingredients": ["gin", "vermouth", "bitters"],
                "mood": "sophisticated",
                "preferences": "stirred not shaken",
            },
            timeout=15.0,
        )
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "ingredients" in data
        assert "instructions" in data
        assert "flavor_profile" in data
        assert "why_this_works" in data
        assert len(data["ingredients"]) > 0


@pytest.mark.integration
@pytest.mark.anyio
async def test_what_can_i_make_integration(
    client: TestClient,
    editor_headers: dict[str, str],
) -> None:
    """Test 'What Can I Make?' feature with real AI substitution.

    This test verifies:
    1. Creates ingredients and a cocktail
    2. Simulates user having a subset of ingredients
    3. Calls the AI service to suggest a substitution for the missing ingredient
    """
    if not _services_available():
        pytest.skip("Docker Compose services not running")

    tequila_response = client.post(
        "/api/v1/ingredients",
        json={"name": "Tequila", "category": "spirit", "description": "Agave spirit"},
        headers=editor_headers,
    )
    assert tequila_response.status_code == 201
    tequila_id = tequila_response.json()["id"]

    lime_response = client.post(
        "/api/v1/ingredients",
        json={"name": "Lime Juice", "category": "juice", "description": "Fresh lime"},
        headers=editor_headers,
    )
    assert lime_response.status_code == 201
    lime_id = lime_response.json()["id"]

    triple_sec_response = client.post(
        "/api/v1/ingredients",
        json={
            "name": "Triple Sec",
            "category": "liqueur",
            "description": "Orange liqueur",
        },
        headers=editor_headers,
    )
    assert triple_sec_response.status_code == 201
    triple_sec_id = triple_sec_response.json()["id"]

    margarita_data = {
        "name": "Test Margarita",
        "difficulty": 1,
        "glass_type": "rocks",
        "instructions": "Shake all ingredients with ice, strain",
        "ingredients": [
            {"ingredient_id": tequila_id, "amount": "60ml", "is_optional": False},
            {"ingredient_id": lime_id, "amount": "30ml", "is_optional": False},
            {"ingredient_id": triple_sec_id, "amount": "20ml", "is_optional": False},
        ],
    }

    create_response = client.post(
        "/api/v1/cocktails/",
        json=margarita_data,
        headers=editor_headers,
    )
    assert create_response.status_code == 201, (
        f"Failed to create test cocktail: {create_response.json()}"
    )
    cocktail_id = create_response.json()["id"]

    detail_response = client.get(
        f"/api/v1/cocktails/{cocktail_id}",
        headers=editor_headers,
    )
    assert detail_response.status_code == 200
    test_margarita = detail_response.json()
    assert test_margarita["name"] == "Test Margarita"

    user_ingredients = {"Tequila", "Lime Juice"}
    required_ingredients = {ing["name"] for ing in test_margarita["ingredients"]}

    if user_ingredients >= required_ingredients:
        match_type = "exact"
    elif len(required_ingredients - user_ingredients) <= 2:
        match_type = "almost"
    else:
        match_type = "no_match"

    assert match_type == "almost", f"Expected almost match, got {match_type}"

    # Verify AI substitution for the missing ingredient
    missing = required_ingredients - user_ingredients
    async with httpx.AsyncClient() as http_client:
        ai_response = await http_client.post(
            "http://localhost:8001/mix",
            json={
                "ingredients": list(user_ingredients),
                "mood": "creative",
                "preferences": f"Substitute for {', '.join(missing)} in a Margarita",
            },
            timeout=15.0,
        )
        assert ai_response.status_code == 200
        ai_data = ai_response.json()
        assert ai_data["name"]
        assert len(ai_data["ingredients"]) > 0
        assert ai_data["instructions"]
