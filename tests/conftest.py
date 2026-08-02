import os

import pytest

# 测试默认使用 SQLite，避免依赖本地 MySQL
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def isolated_stream_capture_config(tmp_path, monkeypatch):
    config_file = tmp_path / "stream_capture_config.json"
    monkeypatch.setenv("STREAM_CAPTURE_CONFIG_PATH", str(config_file))
    yield config_file


@pytest.fixture(autouse=True)
def isolated_sensor_config(tmp_path, monkeypatch):
    config_file = tmp_path / "sensor_config.json"
    monkeypatch.setenv("SENSOR_CONFIG_PATH", str(config_file))
    yield config_file


@pytest.fixture(autouse=True)
def isolated_weight_tare(tmp_path, monkeypatch):
    tare_file = tmp_path / "weight_tare.json"
    monkeypatch.setenv("WEIGHT_TARE_PATH", str(tare_file))
    from app.services.weight_tare_store import reset_tare_offset_cache

    reset_tare_offset_cache()
    yield tare_file
    reset_tare_offset_cache()


@pytest.fixture(autouse=True)
def reset_database():
    from app.core.config import get_settings
    from app.db.session import reset_database_runtime

    get_settings.cache_clear()
    reset_database_runtime()
    yield
    reset_database_runtime()
    get_settings.cache_clear()
