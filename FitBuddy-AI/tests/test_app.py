import os

os.environ["DEMO_MODE"] = "true"

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_generate():
    payload = {
        "user_id": "TEST001",
        "username": "Test User",
        "age": 18,
        "weight": 60,
        "goal": "general wellness",
        "intensity": "low",
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["user_id"] == "TEST001"
    assert "Day 1" in data["plan"]


def test_api_feedback():
    payload = {
        "user_id": "TEST001",
        "feedback": "Make the plan gentler and include more recovery.",
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    assert "Updated" in response.json()["user"]["updated_plan"]
