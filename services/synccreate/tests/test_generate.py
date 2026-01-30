import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_generate_creative():
    client = TestClient(app)
    resp = client.post("/generate", json={
        "prompt": "A cat riding a bike",
        "user_id": "testuser",
        "style": "cartoon",
        "num_images": 1
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "image_urls" in data
    assert isinstance(data["image_urls"], list)
    assert data["job_id"]
