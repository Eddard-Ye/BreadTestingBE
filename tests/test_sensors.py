from fastapi.testclient import TestClient


def test_get_current_temperature(client: TestClient) -> None:
    response = client.get("/api/v1/sensors/temperature")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["value"], float)
    assert 0 <= data["value"] <= 100
    assert data["connected"] is True


def test_get_current_weight(client: TestClient) -> None:
    response = client.get("/api/v1/sensors/weight")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["value"], float)
    assert 0 <= data["value"] <= 100
    assert data["connected"] is True
