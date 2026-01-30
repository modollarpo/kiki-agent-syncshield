"""
Unit tests for SyncBrain FastAPI app
"""



import sys
import os
import pytest
from fastapi.testclient import TestClient
# Add proto output dir to sys.path for brain_pb2 imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../shared/types/python/brain')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from main import app, conversation_memory

client = TestClient(app)

def test_health_check():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

import openai
from unittest.mock import patch

import httpx

def test_plan_strategy_valid():
    os.environ["OPENAI_API_KEY"] = "demo-key"
    fake_response = type("FakeResponse", (), {"choices": [type("Choice", (), {"message": type("Msg", (), {"content": "Increase ad spend on high-LTV segments."})()})]})()
    with patch("openai.chat.completions.create", return_value=fake_response):
        resp = client.post("/plan-strategy", json={"user_id": "u1", "context": {"goal": "maximize LTV"}})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "planned"
        assert data["user_id"] == "u1"
        assert "plan" in data
        # Conversation memory updated
        assert "plan" in conversation_memory["u1"][-1]

def test_plan_strategy_invalid_context():
    resp = client.post("/plan-strategy", json={"user_id": "u2", "context": {}})
    assert resp.status_code == 400
    assert "Context is required" in resp.text


def test_coordinate_agents_success():
    # Only mock httpx.Client.post for external agent URLs
    real_post = httpx.Client.post
    def fake_post(self, url, *args, **kwargs):
        if isinstance(url, str) and ("syncvalue" in url or "syncflow" in url or "synccreate" in url):
            if "syncvalue" in url:
                return type("Resp", (), {"json": lambda: {"ltv": 123}, "raise_for_status": lambda: None})()
            if "syncflow" in url:
                return type("Resp", (), {"json": lambda: {"bid": "ok"}, "raise_for_status": lambda: None})()
            if "synccreate" in url:
                return type("Resp", (), {"json": lambda: {"creative_id": "c1"}, "raise_for_status": lambda: None})()
        return real_post(self, url, *args, **kwargs)
    with patch.object(httpx.Client, "post", new=fake_post):
        resp = client.post("/coordinate-agents", json={
            "agents": ["syncvalue", "syncflow", "synccreate"],
            "task": "test",
            "context": {"user_id": "u1", "creative_prompt": "banner"}
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "coordinated"
        assert "syncvalue" in data["results"]
        assert "synccreate" in data["results"]
        assert "syncflow" in data["results"]

def test_plan_strategy_llm_error(monkeypatch):
    # Simulate OpenAI error
    def fake_create(*a, **kw):
        raise Exception("LLM down")
    import openai
    monkeypatch.setattr(openai.Completion, "create", fake_create)
    resp = client.post("/plan-strategy", json={"user_id": "u3", "context": {"goal": "test"}})
    assert resp.status_code == 500
    assert "LLM service error" in resp.text

def test_coordinate_agents():
    resp = client.post("/coordinate-agents", json={"agents": ["a1"], "task": "t1", "context": {}})
    assert resp.status_code == 200
    assert resp.json()["status"] == "coordinated"

def test_evaluate_performance():
    resp = client.post("/evaluate-performance", json={"session_id": "s1", "metrics": {}})
    assert resp.status_code == 200
    assert resp.json()["status"] == "evaluated"
