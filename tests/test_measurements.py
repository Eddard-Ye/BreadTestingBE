from fastapi.testclient import TestClient

from tests.test_recipes import NEW_RECIPE, _auth_headers


def _create_test_recipe(client: TestClient) -> str:
    headers = _auth_headers(client)
    create = client.post("/api/v1/recipes", json=NEW_RECIPE, headers=headers)
    assert create.status_code == 201
    return create.json()["id"]


def _sample_measurement(recipe_id: str, record_type: str = "product", slot_index: int = 0):
    return {
        "recipeId": recipe_id,
        "recordType": record_type,
        "slotIndex": slot_index,
        "sampleName": f"测试配方-成品-{slot_index + 1}",
        "temperature": "24.5",
        "weight": "128.30",
        "length": "101.2",
        "width": "49.5",
        "height": "29.8",
        "waterCutWidth": "0",
    }


def test_list_measurements_empty(client: TestClient) -> None:
    response = client.get("/api/v1/measurements")
    assert response.status_code == 200
    data = response.json()
    assert data["records"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["pageSize"] == 10


def test_create_batch_and_list_measurement(client: TestClient) -> None:
    recipe_id = _create_test_recipe(client)
    batch = {
        "records": [
            _sample_measurement(recipe_id, slot_index=0),
            {**_sample_measurement(recipe_id, slot_index=1), "sampleName": "测试配方-成品-2"},
        ]
    }
    create = client.post("/api/v1/measurements/batch", json=batch)
    assert create.status_code == 201
    created = create.json()
    assert len(created) == 2

    list_all = client.get("/api/v1/measurements")
    assert list_all.status_code == 200
    assert list_all.json()["total"] == 2

    list_filtered = client.get(
        "/api/v1/measurements",
        params={"recipeId": recipe_id, "recordType": "product"},
    )
    assert list_filtered.status_code == 200
    assert list_filtered.json()["total"] == 2


def test_list_measurements_pagination(client: TestClient) -> None:
    recipe_id = _create_test_recipe(client)
    batch = {
        "records": [
            {**_sample_measurement(recipe_id, slot_index=i), "sampleName": f"测试配方-成品-{i + 1}"}
            for i in range(12)
        ]
    }
    client.post("/api/v1/measurements/batch", json=batch)

    page1 = client.get(
        "/api/v1/measurements",
        params={"recipeId": recipe_id, "recordType": "product", "page": 1, "pageSize": 10},
    )
    assert page1.status_code == 200
    data = page1.json()
    assert data["total"] == 12
    assert len(data["records"]) == 10
    assert data["page"] == 1
    assert data["pageSize"] == 10

    page2 = client.get(
        "/api/v1/measurements",
        params={"recipeId": recipe_id, "recordType": "product", "page": 2, "pageSize": 10},
    )
    assert page2.status_code == 200
    assert len(page2.json()["records"]) == 2


def test_create_batch_unknown_recipe(client: TestClient) -> None:
    batch = {"records": [_sample_measurement("missing")]}
    response = client.post("/api/v1/measurements/batch", json=batch)
    assert response.status_code == 404
