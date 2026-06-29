from unittest.mock import MagicMock

from fastapi.testclient import TestClient


def test_capture_measurement_success(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.stream_capture_service.read_temperature",
        lambda: MagicMock(value=61.7, connected=True),
    )
    monkeypatch.setattr(
        "app.services.stream_capture_service.read_weight",
        lambda: MagicMock(value=90.57, connected=True),
    )

    class FakeResponse:
        content = (
            b'{"ok": true, "length_mm": 101.9, "width_mm": 51.2, "water_cut_mm": 42.5}'
        )

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "ok": True,
                "fileName": "test.jpg",
                "name": "测试配方-成品-1",
                "water_cut": True,
                "detections": 1,
                "length_mm": 101.9,
                "width_mm": 51.2,
                "water_cut_mm": 42.5,
            }

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

        def post(self, url: str, json: dict) -> FakeResponse:
            assert url.endswith("/capture")
            assert json == {
                "name": "测试配方-成品-1",
                "height": "0.0mm",
                "temperature": "61.7",
                "weight": "90.57g",
                "water_cut": True,
            }
            return FakeResponse()

    monkeypatch.setattr("app.services.stream_capture_service.httpx.Client", FakeClient)

    response = client.post(
        "/api/v1/capture/measurement",
        json={"name": "测试配方-成品-1", "waterCut": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["temperature"] == "61.7"
    assert data["weight"] == "90.57"
    assert data["height"] == "0.0"
    assert data["length"] == "101.9"
    assert data["width"] == "51.2"
    assert data["waterCutMm"] == "42.5"
    assert data["fileName"] == "test.jpg"
    assert data["imagePreviewUrl"] == "/api/v1/capture/preview/test.jpg"


def test_capture_measurement_water_cut_disabled(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.stream_capture_service.read_temperature",
        lambda: MagicMock(value=25.0, connected=True),
    )
    monkeypatch.setattr(
        "app.services.stream_capture_service.read_weight",
        lambda: MagicMock(value=12.3, connected=True),
    )

    captured_payload: dict = {}

    class FakeResponse:
        content = b'{"ok": true, "length_mm": 122.3, "width_mm": 62.9, "water_cut_mm": null}'

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "ok": True,
                "fileName": "bread1_20260625_003728.jpg",
                "name": "bread1",
                "water_cut": False,
                "record": {
                    "lw": "LxW: 122.3mm x 62.9mm",
                    "height": "10",
                    "temperature": "10°C",
                    "weight": "20",
                    "water_cut": None,
                },
                "detections": 1,
                "length_mm": 122.3,
                "width_mm": 62.9,
                "water_cut_mm": None,
            }

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

        def post(self, url: str, json: dict) -> FakeResponse:
            captured_payload.update(json)
            return FakeResponse()

    monkeypatch.setattr("app.services.stream_capture_service.httpx.Client", FakeClient)

    response = client.post(
        "/api/v1/capture/measurement",
        json={"name": "测试配方-底片-1", "waterCut": False},
    )
    assert response.status_code == 200
    assert captured_payload["water_cut"] is False
    data = response.json()
    assert data["length"] == "122.3"
    assert data["width"] == "62.9"
    assert data["waterCutMm"] == "0"
    assert data["fileName"] == "bread1_20260625_003728.jpg"
    assert data["imagePreviewUrl"] == "/api/v1/capture/preview/bread1_20260625_003728.jpg"
