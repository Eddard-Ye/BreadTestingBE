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


def test_list_measurements_time_filter(client: TestClient) -> None:
    recipe_id = _create_test_recipe(client)
    batch = {
        "records": [
            {
                **_sample_measurement(recipe_id, slot_index=0),
                "recordedAt": "2026-06-22T16:32:56",
            }
        ]
    }
    create = client.post("/api/v1/measurements/batch", json=batch)
    assert create.status_code == 201

    # 本地墙钟范围筛选（与 UI datetime-local 一致，不做 UTC 转换）
    filtered = client.get(
        "/api/v1/measurements",
        params={
            "recipeId": recipe_id,
            "recordType": "product",
            "startTime": "2026-06-22T16:10:00",
            "endTime": "2026-06-22T18:10:59",
        },
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1

    # 旧版前端若发送 UTC ISO，后端也应能正确匹配本地录入时间
    filtered_utc = client.get(
        "/api/v1/measurements",
        params={
            "recipeId": recipe_id,
            "recordType": "product",
            "startTime": "2026-06-22T08:10:00.000Z",
            "endTime": "2026-06-22T10:10:59.000Z",
        },
    )
    assert filtered_utc.status_code == 200
    assert filtered_utc.json()["total"] == 1


def test_list_measurements_has_preview_filter(client: TestClient) -> None:
    recipe_id = _create_test_recipe(client)
    batch = {
        "records": [
            {
                **_sample_measurement(recipe_id, slot_index=0),
                "previewName": "bread1.jpg",
            },
            _sample_measurement(recipe_id, slot_index=1),
        ]
    }
    client.post("/api/v1/measurements/batch", json=batch)

    filtered = client.get("/api/v1/measurements", params={"hasPreview": True})
    assert filtered.status_code == 200
    data = filtered.json()
    assert data["total"] == 1
    assert data["records"][0]["previewName"] == "bread1.jpg"


def test_create_batch_persists_preview_name(client: TestClient) -> None:
    recipe_id = _create_test_recipe(client)
    batch = {
        "records": [
            {
                **_sample_measurement(recipe_id, slot_index=0),
                "previewName": "bread1_20260625_003728.jpg",
            }
        ]
    }
    create = client.post("/api/v1/measurements/batch", json=batch)
    assert create.status_code == 201
    created = create.json()
    assert created[0]["previewName"] == "bread1_20260625_003728.jpg"


def test_create_batch_unknown_recipe(client: TestClient) -> None:
    batch = {"records": [_sample_measurement("missing")]}
    response = client.post("/api/v1/measurements/batch", json=batch)
    assert response.status_code == 404


def test_export_measurements_csv(client: TestClient) -> None:
    recipe_id = _create_test_recipe(client)
    batch = {
        "records": [
            {**_sample_measurement(recipe_id, slot_index=i), "sampleName": f"测试配方-成品-{i + 1}"}
            for i in range(12)
        ]
    }
    client.post("/api/v1/measurements/batch", json=batch)

    response = client.get(
        "/api/v1/measurements/export",
        params={"recipeId": recipe_id, "recordType": "product"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers.get("content-disposition", "")

    body = response.content.decode("utf-8-sig")
    lines = body.strip().splitlines()
    assert lines[0].startswith("名称,温度")
    assert len(lines) == 13  # header + 12 rows


def test_export_measurements_respects_time_filter(client: TestClient) -> None:
    recipe_id = _create_test_recipe(client)
    batch = {
        "records": [
            {
                **_sample_measurement(recipe_id, slot_index=0),
                "recordedAt": "2026-06-22T16:32:56",
            },
            {
                **_sample_measurement(recipe_id, slot_index=1),
                "sampleName": "测试配方-成品-2",
                "recordedAt": "2026-07-01T10:00:00",
            },
        ]
    }
    client.post("/api/v1/measurements/batch", json=batch)

    response = client.get(
        "/api/v1/measurements/export",
        params={
            "recipeId": recipe_id,
            "recordType": "product",
            "startTime": "2026-06-22T16:10:00",
            "endTime": "2026-06-22T18:10:59",
        },
    )
    assert response.status_code == 200
    body = response.content.decode("utf-8-sig")
    lines = [line for line in body.strip().splitlines() if line]
    assert len(lines) == 2  # header + 1 row
