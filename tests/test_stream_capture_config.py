from fastapi.testclient import TestClient


def test_get_stream_capture_config_seeds_from_env(client: TestClient, isolated_stream_capture_config) -> None:
    assert not isolated_stream_capture_config.exists()

    response = client.get("/api/v1/capture/config")
    assert response.status_code == 200
    data = response.json()
    assert data["host"] == "10.172.158.124"
    assert data["port"] == 8080
    assert data["timeoutSeconds"] == 120.0
    assert isolated_stream_capture_config.exists()


def test_update_stream_capture_config_persists(client: TestClient, isolated_stream_capture_config) -> None:
    client.get("/api/v1/capture/config")

    response = client.put(
        "/api/v1/capture/config",
        json={"host": "192.168.1.100", "port": 9090},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["host"] == "192.168.1.100"
    assert data["port"] == 9090

    saved = client.get("/api/v1/capture/config").json()
    assert saved["host"] == "192.168.1.100"
    assert saved["port"] == 9090


def test_capture_measurement_uses_saved_stream_config(
    client: TestClient,
    monkeypatch,
    isolated_stream_capture_config,
) -> None:
    from unittest.mock import MagicMock

    client.put(
        "/api/v1/capture/config",
        json={"host": "10.0.0.8", "port": 9001},
    )

    monkeypatch.setattr(
        "app.services.stream_capture_service.read_temperature",
        lambda: MagicMock(value=25.0, connected=True),
    )
    monkeypatch.setattr(
        "app.services.stream_capture_service.read_weight",
        lambda: MagicMock(value=12.3, connected=True),
    )

    captured_url: dict[str, str] = {}

    class FakeResponse:
        content = b'{"ok": true, "length_mm": 10.0, "width_mm": 20.0, "water_cut_mm": 0}'

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "ok": True,
                "fileName": "test.jpg",
                "length_mm": 10.0,
                "width_mm": 20.0,
                "water_cut_mm": 0,
            }

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

        def post(self, url: str, json: dict) -> FakeResponse:
            captured_url["url"] = url
            return FakeResponse()

    monkeypatch.setattr("app.services.stream_capture_service.httpx.Client", FakeClient)

    response = client.post(
        "/api/v1/capture/measurement",
        json={"name": "测试配方-成品-1", "waterCut": False},
    )
    assert response.status_code == 200
    assert captured_url["url"] == "http://10.0.0.8:9001/capture"
