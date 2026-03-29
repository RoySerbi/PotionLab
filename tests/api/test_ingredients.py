from fastapi.testclient import TestClient


def test_create_ingredient(client: TestClient, auth_headers: dict[str, str]):
    """Test POST /api/v1/ingredients endpoint creates ingredient successfully."""
    payload = {
        "name": "Gin",
        "category": "spirit",
        "description": "London Dry Gin",
        "flavor_tag_ids": [],
    }
    response = client.post("/api/v1/ingredients", json=payload, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Gin"
    assert data["category"] == "spirit"
    assert data["description"] == "London Dry Gin"
    assert "id" in data


def test_list_ingredients(client: TestClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/ingredients returns list of ingredients."""
    client.post(
        "/api/v1/ingredients",
        json={
            "name": "Vodka",
            "category": "spirit",
            "description": "Neutral spirit",
            "flavor_tag_ids": [],
        },
        headers=auth_headers,
    )

    response = client.get("/api/v1/ingredients", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_ingredient_by_id(client: TestClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/ingredients/{id} returns ingredient with nested tags."""
    create_response = client.post(
        "/api/v1/ingredients",
        json={
            "name": "Rum",
            "category": "spirit",
            "description": "Caribbean rum",
            "flavor_tag_ids": [],
        },
        headers=auth_headers,
    )
    ingredient_id = create_response.json()["id"]

    response = client.get(f"/api/v1/ingredients/{ingredient_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ingredient_id
    assert data["name"] == "Rum"
    assert "flavor_tags" in data


def test_get_ingredient_not_found(client: TestClient, auth_headers: dict[str, str]):
    """Test GET /api/v1/ingredients/{id} returns 404 for missing ingredient."""
    response = client.get("/api/v1/ingredients/999", headers=auth_headers)
    assert response.status_code == 404


def test_update_ingredient(client: TestClient, auth_headers: dict[str, str]):
    """Test PUT /api/v1/ingredients/{id} updates ingredient."""
    create_response = client.post(
        "/api/v1/ingredients",
        json={
            "name": "Tequila",
            "category": "spirit",
            "description": "Blanco tequila",
            "flavor_tag_ids": [],
        },
        headers=auth_headers,
    )
    ingredient_id = create_response.json()["id"]

    update_payload = {
        "name": "Tequila",
        "category": "spirit",
        "description": "Reposado tequila",
        "flavor_tag_ids": [],
    }
    response = client.put(
        f"/api/v1/ingredients/{ingredient_id}",
        json=update_payload,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Reposado tequila"


def test_update_ingredient_not_found(client: TestClient, auth_headers: dict[str, str]):
    """Test PUT /api/v1/ingredients/{id} returns 404 for missing ingredient."""
    response = client.put(
        "/api/v1/ingredients/999",
        json={
            "name": "Test",
            "category": "spirit",
            "description": "Test",
            "flavor_tag_ids": [],
        },
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_delete_ingredient(client: TestClient, auth_headers: dict[str, str]):
    """Test DELETE /api/v1/ingredients/{id} removes ingredient."""
    create_response = client.post(
        "/api/v1/ingredients",
        json={
            "name": "Whiskey",
            "category": "spirit",
            "description": "Bourbon whiskey",
            "flavor_tag_ids": [],
        },
        headers=auth_headers,
    )
    ingredient_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/ingredients/{ingredient_id}", headers=auth_headers
    )
    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/ingredients/{ingredient_id}", headers=auth_headers
    )
    assert get_response.status_code == 404


def test_delete_ingredient_not_found(client: TestClient, auth_headers: dict[str, str]):
    """Test DELETE /api/v1/ingredients/{id} returns 404 for missing ingredient."""
    response = client.delete("/api/v1/ingredients/999", headers=auth_headers)
    assert response.status_code == 404
