from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_message_flow():
    resp = client.post("/message", json={"message": "I have stage 2 breast cancer in California"})
    assert resp.status_code == 200
    body = resp.json()
    assert "response" in body