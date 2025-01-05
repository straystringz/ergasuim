from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register():
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User successfully registered"}


def test_login():
    client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
        },
    )
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_invalid_login():
    client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
        },
    )
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}
