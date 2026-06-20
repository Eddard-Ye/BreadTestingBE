from fastapi.testclient import TestClient


def test_login_success(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 600
    assert isinstance(data["access_token"], str)
    assert data["access_token"]


def test_login_wrong_password(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "口令错误"


def test_login_empty_password(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"password": ""})
    assert response.status_code == 422


def test_login_password_with_whitespace(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"password": " admin123 "})
    assert response.status_code == 200


def test_login_fullwidth_password(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"password": "ａｄｍｉｎ１２３"})
    assert response.status_code == 200
