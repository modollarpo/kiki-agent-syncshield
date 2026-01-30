"""
Integration/E2E tests for KIKI Agent API Gateway
"""

import sys
import os
import pytest

from unittest.mock import patch
import jwt
import json

# List of all services for healthz/metrics checks
SERVICES = [
    "syncbrain",
    "syncvalue",
    "syncflow",
    "synccreate",
    "syncengage",
    "syncshield"
]

@pytest.mark.parametrize("service", SERVICES)
def test_service_healthz_and_metrics(service):
    token = make_jwt()
    # /healthz
    resp = client.get(f"/api/{service}/healthz", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json().get("status") == "ok"
    # /metrics
    resp = client.get(f"/api/{service}/metrics", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "prometheus" in resp.text or "_total" in resp.text or "_seconds" in resp.text

# Cross-service call test (SyncBrain coordinates SyncValue and SyncFlow)
@patch("httpx.AsyncClient.request")
def test_cross_service_coordination(mock_request):
    # Mock downstream agent responses
    def side_effect(method, url, headers=None, content=None, **kwargs):
        if "syncvalue" in url:
            return MockResponse({"ltv": 123.45, "user_id": "u1"})
        if "syncflow" in url:
            return MockResponse({"status": "executed", "bid": 42})
        return MockResponse({"result": "ok"})
    mock_request.side_effect = side_effect
    token = make_jwt()
    payload = {
        "agents": ["syncvalue", "syncflow"],
        "task": "run_campaign",
        "context": {"user_id": "u1", "budget": 1000}
    }
    resp = client.post(
        "/api/syncbrain/coordinate-agents",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "coordinated"
    assert "syncvalue" in data["results"]
    assert "syncflow" in data["results"]
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

JWT_SECRET = "supersecretkey"
JWT_ALGORITHM = "HS256"

def make_jwt(payload=None):
    if payload is None:
        payload = {"sub": "testuser"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Mock downstream service responses
class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code
    def json(self):
        return self._json

@patch("httpx.AsyncClient.request")
def test_strategy_planning_flow(mock_request):
    # Mock SyncBrain response
    mock_request.return_value = MockResponse({
        "status": "planned",
        "user_id": "u1",
        "plan": "Increase ad spend on high-LTV segments."
    })
    token = make_jwt()
    resp = client.post(
        "/api/syncbrain/plan-strategy",
        json={"user_id": "u1", "context": {"goal": "maximize LTV"}},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "planned"
    assert "plan" in data

@patch("httpx.AsyncClient.request")
def test_creative_generation_flow(mock_request):
    # Mock SyncCreate response
    mock_request.return_value = MockResponse({
        "creative_id": "c123", "status": "generated"
    })
    token = make_jwt()
    resp = client.post(
        "/api/synccreate/generate",
        json={"prompt": "banner", "user_id": "u1"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "generated"
    assert "creative_id" in data

@patch("httpx.AsyncClient.request")
def test_compliance_audit_flow(mock_request):
    # Mock SyncShield response
    mock_request.return_value = MockResponse({
        "status": "audited", "event": "plan_executed"
    })
    token = make_jwt()
    resp = client.post(
        "/api/syncshield/audit",
        json={"event": "plan_executed", "user_id": "u1", "data": {}},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "audited"
    assert data["event"] == "plan_executed"

def test_missing_jwt():
    resp = client.post("/api/syncbrain/plan-strategy", json={"user_id": "u1", "context": {"goal": "maximize LTV"}})
    assert resp.status_code == 401
    assert "Authorization" in resp.text or "token" in resp.text

def test_invalid_jwt():
    resp = client.post(
        "/api/syncbrain/plan-strategy",
        json={"user_id": "u1", "context": {"goal": "maximize LTV"}},
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert resp.status_code == 401
    assert "Invalid" in resp.text or "expired" in resp.text
