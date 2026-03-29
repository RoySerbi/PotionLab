from typing import Any

import pytest
from fastapi.testclient import TestClient


def test_create_cocktail_with_nested_ingredients(
    client: TestClient, editor_headers: dict[str, str], admin_headers: dict[str, str]
):
    """Test POST /api/v1/cocktails creates cocktail with nested ingredients."""
    ing_one = client.post(
        "/api/v1/ingredients",
        json={"name": "Gin", "category": "spirit", "description": "Dry gin"},
        headers=editor_headers,
    )
    ing_two = client.post(
        "/api/v1/ingredients",
        json={
            "name": "Tonic Water",
            "category": "mixer",
            "description": "Bitter tonic",
        },
        headers=editor_headers,
    )

    assert ing_one.status_code == 201
    assert ing_two.status_code == 201

    payload = {
        "name": "Gin & Tonic",
        "description": "Classic highball",
        "instructions": "Build in glass with ice",
        "glass_type": "Highball",
        "difficulty": 1,
        "ingredients": [
            {
                "ingredient_id": ing_one.json()["id"],
                "amount": "2 oz",
                "is_optional": False,
            },
            {
                "ingredient_id": ing_two.json()["id"],
                "amount": "4 oz",
                "is_optional": False,
            },
        ],
    }

    create_response = client.post(
        "/api/v1/cocktails", json=payload, headers=editor_headers
    )
    assert create_response.status_code == 201
    cocktail_id = create_response.json()["id"]

    detail_response = client.get(
        f"/api/v1/cocktails/{cocktail_id}", headers=editor_headers
    )
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()

    assert detail_payload["name"] == payload["name"]
    assert len(detail_payload["ingredients"]) == 2
    assert {item["name"] for item in detail_payload["ingredients"]} == {
        "Gin",
        "Tonic Water",
    }


def test_list_cocktails(client: TestClient, editor_headers: dict[str, str]):
    """Test GET /api/v1/cocktails returns list of cocktails."""
    ing = client.post(
        "/api/v1/ingredients",
        json={"name": "Vodka", "category": "spirit", "description": "Neutral spirit"},
        headers=editor_headers,
    )
    assert ing.status_code == 201

    payload = {
        "name": "Vodka Martini",
        "description": "Shaken not stirred",
        "instructions": "Shake with ice",
        "glass_type": "Martini",
        "difficulty": 2,
        "ingredients": [
            {
                "ingredient_id": ing.json()["id"],
                "amount": "2.5 oz",
                "is_optional": False,
            }
        ],
    }
    client.post("/api/v1/cocktails", json=payload, headers=editor_headers)

    response = client.get("/api/v1/cocktails", headers=editor_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_cocktail_by_id(client: TestClient, editor_headers: dict[str, str]):
    """Test GET /api/v1/cocktails/{id} returns full cocktail with ingredients."""
    ing = client.post(
        "/api/v1/ingredients",
        json={"name": "Rum", "category": "spirit", "description": "Caribbean rum"},
        headers=editor_headers,
    )
    assert ing.status_code == 201

    payload = {
        "name": "Rum Punch",
        "description": "Tropical delight",
        "instructions": "Mix and serve over ice",
        "glass_type": "Hurricane",
        "difficulty": 1,
        "ingredients": [
            {"ingredient_id": ing.json()["id"], "amount": "2 oz", "is_optional": False}
        ],
    }
    create_response = client.post(
        "/api/v1/cocktails", json=payload, headers=editor_headers
    )
    assert create_response.status_code == 201
    cocktail_id = create_response.json()["id"]

    response = client.get(f"/api/v1/cocktails/{cocktail_id}", headers=editor_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == cocktail_id
    assert data["name"] == "Rum Punch"
    assert "ingredients" in data
    assert "flavor_profile" in data


def test_get_cocktail_not_found(client: TestClient, editor_headers: dict[str, str]):
    """Test GET /api/v1/cocktails/{id} returns 404 for missing cocktail."""
    response = client.get("/api/v1/cocktails/999", headers=editor_headers)
    assert response.status_code == 404


def test_update_cocktail(client: TestClient, editor_headers: dict[str, str]):
    """Test PUT /api/v1/cocktails/{id} updates cocktail."""
    ing = client.post(
        "/api/v1/ingredients",
        json={"name": "Tequila", "category": "spirit", "description": "Blanco tequila"},
        headers=editor_headers,
    )
    assert ing.status_code == 201
    ing_id = ing.json()["id"]

    payload = {
        "name": "Margarita",
        "description": "Classic sour",
        "instructions": "Shake with ice",
        "glass_type": "Coupe",
        "difficulty": 2,
        "ingredients": [
            {"ingredient_id": ing_id, "amount": "2 oz", "is_optional": False}
        ],
    }
    create_response = client.post(
        "/api/v1/cocktails", json=payload, headers=editor_headers
    )
    assert create_response.status_code == 201
    cocktail_id = create_response.json()["id"]

    update_payload = {
        "name": "Margarita",
        "description": "Updated classic sour with lime",
        "instructions": "Shake vigorously with ice",
        "glass_type": "Coupe",
        "difficulty": 2,
        "ingredients": [
            {"ingredient_id": ing_id, "amount": "2.5 oz", "is_optional": False}
        ],
    }
    response = client.put(
        f"/api/v1/cocktails/{cocktail_id}",
        json=update_payload,
        headers=editor_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated classic sour with lime"


def test_update_cocktail_not_found(client: TestClient, editor_headers: dict[str, str]):
    """Test PUT /api/v1/cocktails/{id} returns 404 for missing cocktail."""
    response = client.put(
        "/api/v1/cocktails/999",
        json={
            "name": "Test",
            "description": "Test",
            "instructions": "Test",
            "glass_type": "Rocks",
            "difficulty": 1,
            "ingredients": [],
        },
        headers=editor_headers,
    )
    assert response.status_code == 404


def test_delete_cocktail(client: TestClient, editor_headers: dict[str, str]):
    """Test DELETE /api/v1/cocktails/{id} removes cocktail."""
    ing = client.post(
        "/api/v1/ingredients",
        json={
            "name": "Whiskey",
            "category": "spirit",
            "description": "Bourbon whiskey",
        },
        headers=editor_headers,
    )
    assert ing.status_code == 201

    payload = {
        "name": "Old Fashioned",
        "description": "Classic whiskey cocktail",
        "instructions": "Stir with ice",
        "glass_type": "Rocks",
        "difficulty": 2,
        "ingredients": [
            {"ingredient_id": ing.json()["id"], "amount": "2 oz", "is_optional": False}
        ],
    }
    create_response = client.post(
        "/api/v1/cocktails", json=payload, headers=editor_headers
    )
    assert create_response.status_code == 201
    cocktail_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/cocktails/{cocktail_id}", headers=editor_headers)
    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/cocktails/{cocktail_id}", headers=editor_headers
    )
    assert get_response.status_code == 404


def test_delete_cocktail_not_found(client: TestClient, editor_headers: dict[str, str]):
    """Test DELETE /api/v1/cocktails/{id} returns 404 for missing cocktail."""
    response = client.delete("/api/v1/cocktails/999", headers=editor_headers)
    assert response.status_code == 404


def test_create_cocktail_with_invalid_ingredient_id(
    client: TestClient, editor_headers: dict[str, str]
):
    """Test POST /api/v1/cocktails returns 400 for invalid ingredient_id."""
    payload = {
        "name": "Bad Cocktail",
        "description": "Should fail",
        "instructions": "Cannot be made",
        "glass_type": "Rocks",
        "difficulty": 1,
        "ingredients": [
            {"ingredient_id": 9999, "amount": "1 oz", "is_optional": False}
        ],
    }
    response = client.post("/api/v1/cocktails", json=payload, headers=editor_headers)
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()


def test_update_cocktail_with_invalid_ingredient_id(
    client: TestClient, editor_headers: dict[str, str]
):
    """Test PUT /api/v1/cocktails/{id} returns 400 for invalid ingredient_id."""
    ing = client.post(
        "/api/v1/ingredients",
        json={"name": "Brandy", "category": "spirit", "description": "Cognac"},
        headers=editor_headers,
    )
    assert ing.status_code == 201

    payload = {
        "name": "Sidecar",
        "description": "Classic",
        "instructions": "Shake",
        "glass_type": "Coupe",
        "difficulty": 2,
        "ingredients": [
            {"ingredient_id": ing.json()["id"], "amount": "2 oz", "is_optional": False}
        ],
    }
    create_response = client.post(
        "/api/v1/cocktails", json=payload, headers=editor_headers
    )
    assert create_response.status_code == 201
    cocktail_id = create_response.json()["id"]

    update_payload = {
        "name": "Sidecar",
        "description": "Updated",
        "instructions": "Shake",
        "glass_type": "Coupe",
        "difficulty": 2,
        "ingredients": [
            {"ingredient_id": 9999, "amount": "2 oz", "is_optional": False}
        ],
    }
    response = client.put(
        f"/api/v1/cocktails/{cocktail_id}",
        json=update_payload,
        headers=editor_headers,
    )
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.parametrize("difficulty", [0, 6, -1])
def test_create_cocktail_invalid_difficulty(
    client: TestClient, difficulty: int, editor_headers: dict[str, str]
):
    """Test POST /api/v1/cocktails returns 422 for invalid difficulty values."""
    ing = client.post(
        "/api/v1/ingredients",
        json={"name": "Test Spirit", "category": "spirit", "description": "Test"},
        headers=editor_headers,
    )
    assert ing.status_code == 201

    payload = {
        "name": "Test Cocktail",
        "description": "Test",
        "instructions": "Test",
        "glass_type": "Rocks",
        "difficulty": difficulty,
        "ingredients": [
            {"ingredient_id": ing.json()["id"], "amount": "1 oz", "is_optional": False}
        ],
    }
    response = client.post("/api/v1/cocktails", json=payload, headers=editor_headers)
    assert response.status_code == 422


@pytest.mark.parametrize("field", ["name", "instructions", "glass_type"])
def test_create_cocktail_missing_required_field(
    client: TestClient, field: str, editor_headers: dict[str, str]
):
    """Test POST /api/v1/cocktails returns 422 for missing required fields."""
    ing = client.post(
        "/api/v1/ingredients",
        json={"name": "Test Spirit", "category": "spirit", "description": "Test"},
        headers=editor_headers,
    )
    assert ing.status_code == 201

    payload = {
        "name": "Test Cocktail",
        "description": "Test",
        "instructions": "Test",
        "glass_type": "Rocks",
        "difficulty": 1,
        "ingredients": [
            {"ingredient_id": ing.json()["id"], "amount": "1 oz", "is_optional": False}
        ],
    }
    del payload[field]
    response = client.post("/api/v1/cocktails", json=payload, headers=editor_headers)
    assert response.status_code == 422


def test_create_cocktail_requires_token(client: TestClient) -> None:
    response = client.post(
        "/api/v1/cocktails",
        json={
            "name": "No Auth",
            "description": "Denied",
            "instructions": "None",
            "glass_type": "Rocks",
            "difficulty": 1,
            "ingredients": [],
        },
    )
    assert response.status_code == 401


def test_list_cocktails_invalid_token_rejected(client: TestClient) -> None:
    response = client.get(
        "/api/v1/cocktails", headers={"Authorization": "Bearer not-a-token"}
    )
    assert response.status_code == 401


def test_list_cocktails_with_valid_token(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get("/api/v1/cocktails", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_reader_cannot_use_admin_delete_user(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    created = client.post(
        "/api/v1/auth/register",
        json={"username": "route-reader-target", "password": "secret123"},
    )
    assert created.status_code == 201

    response = client.delete(
        "/api/v1/auth/users/route-reader-target", headers=auth_headers
    )
    assert response.status_code == 403


def test_admin_can_use_admin_delete_user(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    created = client.post(
        "/api/v1/auth/register",
        json={"username": "route-admin-target", "password": "secret123"},
    )
    assert created.status_code == 201

    response = client.delete(
        "/api/v1/auth/users/route-admin-target", headers=admin_headers
    )
    assert response.status_code == 204


def test_auth_me_returns_reader_role(
    client: TestClient, editor_headers: dict[str, str]
) -> None:
    response = client.get("/api/v1/auth/me", headers=editor_headers)
    assert response.status_code == 200
    payload: dict[str, Any] = response.json()
    assert payload["role"] == "editor"


def test_create_cocktail_reader_role_forbidden(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Test POST /api/v1/cocktails returns 403 for reader role."""
    response = client.post(
        "/api/v1/cocktails",
        json={
            "name": "Test",
            "description": "Test",
            "instructions": "Test",
            "glass_type": "Rocks",
            "difficulty": 1,
            "ingredients": [],
        },
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_delete_cocktail_reader_role_forbidden(
    client: TestClient, auth_headers: dict[str, str], editor_headers: dict[str, str]
) -> None:
    """Test DELETE /api/v1/cocktails/{id} returns 403 for reader role."""
    # Create cocktail with editor
    ing = client.post(
        "/api/v1/ingredients",
        json={"name": "Gin", "category": "spirit", "description": "Gin"},
        headers=editor_headers,
    )
    payload = {
        "name": "Gin Tonic",
        "description": "Test",
        "instructions": "Mix",
        "glass_type": "Highball",
        "difficulty": 1,
        "ingredients": [
            {"ingredient_id": ing.json()["id"], "amount": "2 oz", "is_optional": False}
        ],
    }
    create = client.post("/api/v1/cocktails", json=payload, headers=editor_headers)
    cocktail_id = create.json()["id"]

    # Try to delete with reader role
    response = client.delete(f"/api/v1/cocktails/{cocktail_id}", headers=auth_headers)
    assert response.status_code == 403
