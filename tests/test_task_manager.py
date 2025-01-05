from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "description": "Test Task Description",
            "due_date": "2025-01-01",
            "priority": 1,
            "completed": False,
        },
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


def test_read_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_task():
    response = client.post(
        "/tasks",
        json={
            "id": 1,
            "title": "Initial Task",
            "description": "Initial Description",
            "due_date": "2025-01-01",
            "priority": 1,
            "completed": False,
        },
    )
    assert response.status_code == 200

    update_response = client.put(
        "/tasks/1",
        json={
            "title": "Updated Task",
            "description": "Updated Description",
            "due_date": "2025-01-01",
            "priority": 1,
            "completed": True,
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Task"


def test_delete_task():
    response = client.post(
        "/tasks",
        json={
            "id": 2,
            "title": "Task to Delete",
            "description": "Description",
            "due_date": "2025-01-01",
            "priority": 1,
            "completed": False,
        },
    )
    assert response.status_code == 200

    delete_response = client.delete("/tasks/2")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Task deleted"}
