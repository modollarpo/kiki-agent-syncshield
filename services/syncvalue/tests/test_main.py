"""
Unit tests for SyncValue FastAPI app
"""

import sys
import os
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from main import app

client = TestClient(app)

def test_health_check():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_predict_ltv_valid():
    # Valid features dict (10 features for input size)
    features = {f"f{i}": float(i) for i in range(10)}
    resp = client.post("/predict-ltv", json={"user_id": "u1", "features": features})
    assert resp.status_code == 200
    data = resp.json()
    assert "ltv" in data
    assert data["user_id"] == "u1"

def test_predict_ltv_empty_features():
    # Edge case: empty features dict
    resp = client.post("/predict-ltv", json={"user_id": "u2", "features": {}})
    assert resp.status_code == 400
    assert "Features must be a non-empty dict" in resp.text

def test_train():
    resp = client.post("/train", json={"dataset_path": "data.csv", "params": {}})
    assert resp.status_code == 200
    assert resp.json()["status"] == "training_started"

def test_metrics():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "accuracy" in resp.json()

def test_predict_ltv_cross_service_valid(monkeypatch):
    # Patch call_syncflow_bid to simulate accepted bid
    from services.syncvalue.app.handlers_ltv import call_syncflow_bid
    monkeypatch.setattr("services.syncvalue.app.handlers_ltv.call_syncflow_bid", lambda user_id: type("BidResponse", (), {"accepted": True, "bid_id": "bid-1", "reason": None})())
    features = {f"f{i}": float(i) for i in range(10)}
    resp = client.post("/predict-ltv", json={"user_id": "u1", "features": features})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ltv"] == 0.8

def test_predict_ltv_cross_service_reject(monkeypatch):
    # Patch call_syncflow_bid to simulate rejected bid
    from services.syncvalue.app.handlers_ltv import call_syncflow_bid
    monkeypatch.setattr("services.syncvalue.app.handlers_ltv.call_syncflow_bid", lambda user_id: type("BidResponse", (), {"accepted": False, "bid_id": "bid-2", "reason": "Low LTV"})())
    features = {f"f{i}": float(i) for i in range(10)}
    resp = client.post("/predict-ltv", json={"user_id": "u2", "features": features})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ltv"] == 0.3

def test_predict_ltv_invalid_features():
    # Stricter validation: features must be non-empty dict
    resp = client.post("/predict-ltv", json={"user_id": "u3", "features": {}})
    assert resp.status_code == 400
    assert "Features must be a non-empty dict" in resp.text
