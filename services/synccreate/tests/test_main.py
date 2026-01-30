"""
Unit tests for SyncCreate FastAPI app
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_generate_and_retrieve():
    # Generate creative
    resp = client.post("/generate", json={"prompt": "ad banner", "variant": "default", "user_id": "u1"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "generated"
    creative_id = data["creative_id"]
    # Retrieve creative
    resp2 = client.get(f"/creative/{creative_id}")
    assert resp2.status_code == 200
    creative = resp2.json()
    assert creative["creative_id"] == creative_id
    assert creative["prompt"] == "ad banner"
    # List creatives
    resp3 = client.get("/creatives")
    assert resp3.status_code == 200
    creatives = resp3.json()["creatives"]
    assert any(c["creative_id"] == creative_id for c in creatives)

def test_generate_brand_safety():
    resp = client.post("/generate", json={"prompt": "unsafe content", "variant": "default", "user_id": "u2"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["brand_safety"] == "unsafe"

def test_rate_and_summary():
    # Generate creative
    resp = client.post("/generate", json={"prompt": "banner", "variant": "default", "user_id": "u3"})
    creative_id = resp.json()["creative_id"]
    # Rate creative
    for rating in [4, 5, 3]:
        r = client.post("/rate-creative", json={"creative_id": creative_id, "rating": rating, "user_id": "u3"})
        assert r.status_code == 200
        assert r.json()["status"] == "rated"
    # Ratings summary
    resp2 = client.get("/ratings/summary")
    assert resp2.status_code == 200
    summary = resp2.json()["ratings_summary"]
    assert creative_id in summary
    assert summary[creative_id]["count"] == 3
    assert abs(summary[creative_id]["average"] - 4.0) < 0.01

def test_rate_creative():
    resp = client.post("/rate-creative", json={"creative_id": "c123", "rating": 5, "user_id": "u1"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "rated"
