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
def reset_database():
    from app.core.config import get_settings
    from app.db.session import reset_database_runtime

    get_settings.cache_clear()
    reset_database_runtime()
    yield
    reset_database_runtime()
    get_settings.cache_clear()
