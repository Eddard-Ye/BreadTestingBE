from fastapi.testclient import TestClient

NEW_RECIPE = {
    "name": "测试配方A",
    "batchSize": 4,
    "temperature": {"min": 20, "max": 30},
    "weight": {"min": 100, "max": 150},
    "length": {"min": 90, "max": 110},
    "width": {"min": 40, "max": 55},
    "height": {"min": 25, "max": 35},
    "waterCutWidth": {"min": 40, "max": 50},
    "enableWaterCut": True,
    "heightCalcMode": "peak",
    "enableBottomMeasurement": False,
    "bottomParams": {
        "batchSize": 0,
        "temperature": {"min": 0, "max": 0},
        "weight": {"min": 0, "max": 0},
        "length": {"min": 0, "max": 0},
        "width": {"min": 0, "max": 0},
        "height": {"min": 0, "max": 0},
        "waterCutWidth": {"min": 0, "max": 0},
        "heightCalcMode": "peak",
    },
    "enableMiddleMeasurement": False,
    "middleParams": {
        "batchSize": 0,
        "temperature": {"min": 0, "max": 0},
        "weight": {"min": 0, "max": 0},
        "length": {"min": 0, "max": 0},
        "width": {"min": 0, "max": 0},
        "height": {"min": 0, "max": 0},
        "waterCutWidth": {"min": 0, "max": 0},
        "heightCalcMode": "peak",
    },
}


def _auth_headers(client: TestClient) -> dict[str, str]:
    login = client.post("/api/v1/auth/login", json={"password": "admin123"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_list_recipes_empty(client: TestClient) -> None:
    response = client.get("/api/v1/recipes")
    assert response.status_code == 200
    data = response.json()
    assert data["recipes"] == {}


def test_list_recipe_options_empty(client: TestClient) -> None:
    response = client.get("/api/v1/recipes/options")
    assert response.status_code == 200
    assert response.json()["options"] == []


def test_get_recipe(client: TestClient) -> None:
    headers = _auth_headers(client)
    create = client.post("/api/v1/recipes", json=NEW_RECIPE, headers=headers)
    assert create.status_code == 201
    recipe_id = create.json()["id"]

    response = client.get(f"/api/v1/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == recipe_id
    assert data["batchSize"] == 4
    assert data["enableWaterCut"] is True


def test_get_recipe_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/recipes/not-exists")
    assert response.status_code == 404


def test_create_recipe_requires_auth(client: TestClient) -> None:
    response = client.post("/api/v1/recipes", json=NEW_RECIPE)
    assert response.status_code == 401


def test_create_update_delete_recipe(client: TestClient) -> None:
    headers = _auth_headers(client)

    create = client.post("/api/v1/recipes", json=NEW_RECIPE, headers=headers)
    assert create.status_code == 201
    created = create.json()
    recipe_id = created["id"]
    assert created["name"] == "测试配方A"
    assert created["enableWaterCut"] is True

    get_created = client.get(f"/api/v1/recipes/{recipe_id}")
    assert get_created.status_code == 200

    updated_payload = {**NEW_RECIPE, "name": "测试配方A-修改", "batchSize": 5}
    update = client.put(f"/api/v1/recipes/{recipe_id}", json=updated_payload, headers=headers)
    assert update.status_code == 200
    assert update.json()["name"] == "测试配方A-修改"
    assert update.json()["batchSize"] == 5

    second = client.post(
        "/api/v1/recipes",
        json={**NEW_RECIPE, "name": "测试配方B"},
        headers=headers,
    )
    assert second.status_code == 201

    delete = client.delete(f"/api/v1/recipes/{recipe_id}", headers=headers)
    assert delete.status_code == 204

    missing = client.get(f"/api/v1/recipes/{recipe_id}")
    assert missing.status_code == 404


def test_cannot_delete_last_recipe(client: TestClient) -> None:
    headers = _auth_headers(client)
    create = client.post("/api/v1/recipes", json=NEW_RECIPE, headers=headers)
    assert create.status_code == 201
    recipe_id = create.json()["id"]

    response = client.delete(f"/api/v1/recipes/{recipe_id}", headers=headers)
    assert response.status_code == 400
