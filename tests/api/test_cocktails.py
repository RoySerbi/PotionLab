from fastapi.testclient import TestClient


def test_create_cocktail_with_nested_ingredients(client: TestClient):
    ing_one = client.post(
        "/api/v1/ingredients",
        json={"name": "Gin", "category": "spirit", "description": "Dry gin"},
    )
    ing_two = client.post(
        "/api/v1/ingredients",
        json={
            "name": "Tonic Water",
            "category": "mixer",
            "description": "Bitter tonic",
        },
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

    create_response = client.post("/api/v1/cocktails", json=payload)
    assert create_response.status_code == 201
    cocktail_id = create_response.json()["id"]

    detail_response = client.get(f"/api/v1/cocktails/{cocktail_id}")
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()

    assert detail_payload["name"] == payload["name"]
    assert len(detail_payload["ingredients"]) == 2
    assert {item["name"] for item in detail_payload["ingredients"]} == {
        "Gin",
        "Tonic Water",
    }
