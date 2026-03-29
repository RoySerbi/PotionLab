from fastapi.testclient import TestClient


def test_create_flavor_tag(client: TestClient):
    """Test POST /api/v1/flavor-tags endpoint creates flavor tag successfully."""
    payload = {"name": "Citrus", "category": "aromatic"}
    response = client.post("/api/v1/flavor-tags", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Citrus"
    assert data["category"] == "aromatic"
    assert "id" in data


def test_create_flavor_tag_duplicate_name(client: TestClient):
    """Test POST /api/v1/flavor-tags returns 409 for duplicate name."""
    payload = {"name": "Sweet", "category": "taste"}
    client.post("/api/v1/flavor-tags", json=payload)

    response = client.post("/api/v1/flavor-tags", json=payload)
    assert response.status_code == 409


def test_list_flavor_tags(client: TestClient):
    """Test GET /api/v1/flavor-tags returns list of flavor tags."""
    client.post("/api/v1/flavor-tags", json={"name": "Herbal", "category": "aromatic"})

    response = client.get("/api/v1/flavor-tags")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_flavor_tag_by_id(client: TestClient):
    """Test GET /api/v1/flavor-tags/{id} returns flavor tag."""
    create_response = client.post(
        "/api/v1/flavor-tags", json={"name": "Spicy", "category": "taste"}
    )
    flavor_tag_id = create_response.json()["id"]

    response = client.get(f"/api/v1/flavor-tags/{flavor_tag_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == flavor_tag_id
    assert data["name"] == "Spicy"


def test_get_flavor_tag_not_found(client: TestClient):
    """Test GET /api/v1/flavor-tags/{id} returns 404 for missing flavor tag."""
    response = client.get("/api/v1/flavor-tags/999")
    assert response.status_code == 404


def test_update_flavor_tag(client: TestClient):
    """Test PUT /api/v1/flavor-tags/{id} updates flavor tag."""
    create_response = client.post(
        "/api/v1/flavor-tags", json={"name": "Bitter", "category": "taste"}
    )
    flavor_tag_id = create_response.json()["id"]

    update_payload = {"name": "Bitter", "category": "flavor"}
    response = client.put(f"/api/v1/flavor-tags/{flavor_tag_id}", json=update_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "flavor"


def test_update_flavor_tag_duplicate_name(client: TestClient):
    """Test PUT /api/v1/flavor-tags/{id} returns 409 for duplicate name."""
    client.post("/api/v1/flavor-tags", json={"name": "Sour", "category": "taste"})
    create_response = client.post(
        "/api/v1/flavor-tags", json={"name": "Salty", "category": "taste"}
    )
    flavor_tag_id = create_response.json()["id"]

    update_payload = {"name": "Sour", "category": "taste"}
    response = client.put(f"/api/v1/flavor-tags/{flavor_tag_id}", json=update_payload)
    assert response.status_code == 409


def test_update_flavor_tag_not_found(client: TestClient):
    """Test PUT /api/v1/flavor-tags/{id} returns 404 for missing flavor tag."""
    response = client.put(
        "/api/v1/flavor-tags/999", json={"name": "Test", "category": "test"}
    )
    assert response.status_code == 404


def test_delete_flavor_tag(client: TestClient):
    """Test DELETE /api/v1/flavor-tags/{id} removes flavor tag."""
    create_response = client.post(
        "/api/v1/flavor-tags", json={"name": "Umami", "category": "taste"}
    )
    flavor_tag_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/flavor-tags/{flavor_tag_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/flavor-tags/{flavor_tag_id}")
    assert get_response.status_code == 404


def test_delete_flavor_tag_not_found(client: TestClient):
    """Test DELETE /api/v1/flavor-tags/{id} returns 404 for missing flavor tag."""
    response = client.delete("/api/v1/flavor-tags/999")
    assert response.status_code == 404
