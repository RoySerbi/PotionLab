"""Tests for PotionLabClient API client."""

from typing import Any
from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.clients import PotionLabClient


@pytest.fixture
def sample_data(client: TestClient) -> dict[str, Any]:
    """Create sample ingredients and cocktail for testing."""
    ing_one = client.post(
        "/api/v1/ingredients",
        json={"name": "Rum", "category": "spirit", "description": "Dark rum"},
    )
    ing_two = client.post(
        "/api/v1/ingredients",
        json={"name": "Lime Juice", "category": "mixer", "description": "Fresh lime"},
    )

    payload = {
        "name": "Daiquiri",
        "description": "Classic rum cocktail",
        "instructions": "Shake and strain",
        "glass_type": "Coupe",
        "difficulty": 1,
        "ingredients": [
            {
                "ingredient_id": ing_one.json()["id"],
                "amount": "2 oz",
                "is_optional": False,
            },
            {
                "ingredient_id": ing_two.json()["id"],
                "amount": "1 oz",
                "is_optional": False,
            },
        ],
    }

    cocktail = client.post("/api/v1/cocktails", json=payload)

    return {
        "cocktail_id": cocktail.json()["id"],
        "ingredient_ids": [ing_one.json()["id"], ing_two.json()["id"]],
    }


def test_list_cocktails_returns_list(
    sample_data: dict[str, Any], client: TestClient
) -> None:
    """Test that list_cocktails returns a list of dicts."""
    list_response = client.get("/api/v1/cocktails/")
    assert list_response.status_code == 200
    result = list_response.json()

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(item, dict) for item in result)
    assert all("id" in item for item in result)
    assert all("name" in item for item in result)


def test_list_ingredients_returns_list(
    sample_data: dict[str, Any], client: TestClient
) -> None:
    """Test that list_ingredients returns a list of dicts."""
    list_response = client.get("/api/v1/ingredients/")
    assert list_response.status_code == 200
    result = list_response.json()

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(item, dict) for item in result)
    assert all("id" in item for item in result)
    assert all("name" in item for item in result)


def test_get_cocktail_returns_detail(
    sample_data: dict[str, Any], client: TestClient
) -> None:
    """Test that get_cocktail returns cocktail dict for valid ID."""
    cocktail_id = sample_data["cocktail_id"]
    response = client.get(f"/api/v1/cocktails/{cocktail_id}")
    assert response.status_code == 200
    result = response.json()

    assert isinstance(result, dict)
    assert result["id"] == cocktail_id
    assert "name" in result
    assert "ingredients" in result


def test_get_cocktail_returns_none_for_invalid_id(client: TestClient) -> None:
    """Test that get_cocktail returns 404 for non-existent ID."""
    response = client.get("/api/v1/cocktails/999999")
    assert response.status_code == 404


def test_api_client_list_cocktails_with_mock() -> None:
    """Test PotionLabClient.list_cocktails with mocked httpx."""
    mock_cocktails = [
        {"id": 1, "name": "Martini"},
        {"id": 2, "name": "Daiquiri"},
    ]

    with patch("app.clients.api_client.httpx.Client") as mock_http:
        mock_response = mock_http.return_value.__enter__.return_value.get.return_value
        mock_response.json.return_value = mock_cocktails

        client = PotionLabClient(base_url="http://example.com")
        result = client.list_cocktails()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "Martini"


def test_api_client_list_ingredients_with_mock() -> None:
    """Test PotionLabClient.list_ingredients with mocked httpx."""
    mock_ingredients = [
        {"id": 1, "name": "Gin", "category": "spirit"},
        {"id": 2, "name": "Vermouth", "category": "fortified"},
    ]

    with patch("app.clients.api_client.httpx.Client") as mock_http:
        mock_response = mock_http.return_value.__enter__.return_value.get.return_value
        mock_response.json.return_value = mock_ingredients

        client = PotionLabClient(base_url="http://example.com")
        result = client.list_ingredients()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "Gin"


def test_api_client_get_cocktail_with_mock() -> None:
    """Test PotionLabClient.get_cocktail with mocked httpx."""
    mock_cocktail = {
        "id": 1,
        "name": "Martini",
        "ingredients": [{"ingredient_id": 1, "amount": "2 oz"}],
    }

    with patch("app.clients.api_client.httpx.Client") as mock_http:
        mock_response = mock_http.return_value.__enter__.return_value.get.return_value
        mock_response.json.return_value = mock_cocktail

        client = PotionLabClient(base_url="http://example.com")
        result = client.get_cocktail(1)

        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["name"] == "Martini"


def test_api_client_get_cocktail_handles_404_with_mock() -> None:
    """Test PotionLabClient.get_cocktail returns None on 404."""
    with patch("app.clients.api_client.httpx.Client") as mock_http:
        mock_response = mock_http.return_value.__enter__.return_value.get.return_value
        mock_response.raise_for_status.side_effect = httpx.HTTPError("404 Not Found")

        client = PotionLabClient(base_url="http://example.com")
        result = client.get_cocktail(999999)

        assert result is None


def test_list_cocktails_graceful_error_handling() -> None:
    """Test that list_cocktails returns empty list on connection error."""
    client = PotionLabClient(base_url="http://localhost:9999")
    result = client.list_cocktails()

    assert result == []
    assert isinstance(result, list)


def test_list_ingredients_graceful_error_handling() -> None:
    """Test that list_ingredients returns empty list on connection error."""
    client = PotionLabClient(base_url="http://localhost:9999")
    result = client.list_ingredients()

    assert result == []
    assert isinstance(result, list)


def test_get_cocktail_graceful_error_handling() -> None:
    """Test that get_cocktail returns None on connection error."""
    client = PotionLabClient(base_url="http://localhost:9999")
    result = client.get_cocktail(1)

    assert result is None
