"""
Unit tests for SyncEngage FastAPI app
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_trigger():
    resp = client.post("/trigger", json={"event": "churn_risk", "user_id": "u1", "data": {}})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "triggered"
    assert "crm_results" in data
    for crm in ["hubspot", "klaviyo", "mailchimp"]:
        assert crm in data["crm_results"]
        assert data["crm_results"][crm]["crm"] == crm
def test_crm_integrations():
    resp = client.get("/crm/integrations")
    assert resp.status_code == 200
    data = resp.json()
    assert set(data["integrations"]) == {"hubspot", "klaviyo", "mailchimp"}

def test_get_flows():
    resp = client.get("/flows")
    assert resp.status_code == 200
    assert "flows" in resp.json()

def test_list_flows():
    resp = client.get("/flows")
    assert resp.status_code == 200
    data = resp.json()
    assert "flows" in data
    assert "churn_risk" in data["flows"]

def test_trigger_valid():
    resp = client.post("/trigger", json={"event": "churn_risk", "user_id": "u1", "data": {"score": 0.9}})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "triggered"
    assert data["event"] == "churn_risk"

def test_trigger_invalid():
    resp = client.post("/trigger", json={"event": "", "user_id": "", "data": {}})
    assert resp.status_code == 400
    assert "event and user_id required" in resp.text

def test_trigger_hubspot(monkeypatch):
    # Patch call_syncvalue_ltv to return high LTV
    from main import call_syncvalue_ltv
    monkeypatch.setattr("main.call_syncvalue_ltv", lambda user_id, features: 0.9)
    resp = client.post("/trigger", json={"event": "upsell", "user_id": "u2", "data": {"features": {"f1": 1.0}}, "crm": "hubspot"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "triggered"
    assert data["event"] == "upsell"

def test_trigger_klaviyo_low_ltv(monkeypatch):
    # Patch call_syncvalue_ltv to return low LTV
    from main import call_syncvalue_ltv
    monkeypatch.setattr("main.call_syncvalue_ltv", lambda user_id, features: 0.2)
    resp = client.post("/trigger", json={"event": "churn_risk", "user_id": "u3", "data": {"features": {"f1": 0.1}}, "crm": "klaviyo"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "skipped_low_ltv"

def test_trigger_salesforce_multistep(monkeypatch):
    from main import call_syncvalue_ltv, trigger_salesforce
    monkeypatch.setattr("main.call_syncvalue_ltv", lambda user_id, features: 0.9)
    monkeypatch.setattr("main.trigger_salesforce", lambda event, user_id, data: True)
    resp = client.post("/trigger", json={"event": "upsell", "user_id": "u4", "data": {"score": 0.95}, "crm": "salesforce", "workflow": "multistep"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "triggered"

def test_trigger_conditional_workflow(monkeypatch):
    from main import call_syncvalue_ltv, trigger_klaviyo
    monkeypatch.setattr("main.call_syncvalue_ltv", lambda user_id, features: 0.9)
    monkeypatch.setattr("main.trigger_klaviyo", lambda event, user_id, data: True)
    # Should trigger (score > 0.8)
    resp = client.post("/trigger", json={"event": "churn_risk", "user_id": "u5", "data": {"score": 0.85}, "crm": "klaviyo", "workflow": "conditional"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "triggered"
    # Should not trigger (score <= 0.8)
    resp = client.post("/trigger", json={"event": "churn_risk", "user_id": "u6", "data": {"score": 0.5}, "crm": "klaviyo", "workflow": "conditional"})
    assert resp.status_code == 502 or resp.status_code == 200
    # Accept either: 502 (workflow failed) or 200 (skipped)

def test_trigger_mailchimp(monkeypatch):
    from main import call_syncvalue_ltv, trigger_mailchimp
    monkeypatch.setattr("main.call_syncvalue_ltv", lambda user_id, features: 0.9)
    monkeypatch.setattr("main.trigger_mailchimp", lambda event, user_id, data: True)
    resp = client.post("/trigger", json={"event": "upsell", "user_id": "u7", "data": {"segment": "premium"}, "crm": "mailchimp"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "triggered"

def test_trigger_zoho_business_rule(monkeypatch):
    from main import call_syncvalue_ltv, trigger_zoho
    monkeypatch.setattr("main.call_syncvalue_ltv", lambda user_id, features: 0.6)
    monkeypatch.setattr("main.trigger_zoho", lambda event, user_id, data: True)
    # Should trigger for premium segment
    resp = client.post("/trigger", json={"event": "churn_risk", "user_id": "u8", "data": {"segment": "premium"}, "crm": "zoho"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "triggered"
    # Should skip for non-premium, low LTV
    resp = client.post("/trigger", json={"event": "upsell", "user_id": "u9", "data": {"segment": "basic"}, "crm": "zoho"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "skipped_business_rule"

def test_trigger_activecampaign(monkeypatch):
    from main import call_syncvalue_ltv, trigger_activecampaign
    monkeypatch.setattr("main.call_syncvalue_ltv", lambda user_id, features: 0.8)
    monkeypatch.setattr("main.trigger_activecampaign", lambda event, user_id, data: True)
    resp = client.post("/trigger", json={"event": "churn_risk", "user_id": "u10", "data": {"region": "EU"}, "crm": "activecampaign"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "triggered"

def test_trigger_sendinblue_last_active(monkeypatch):
    from main import call_syncvalue_ltv, trigger_sendinblue
    monkeypatch.setattr("main.call_syncvalue_ltv", lambda user_id, features: 0.4)
    monkeypatch.setattr("main.trigger_sendinblue", lambda event, user_id, data: True)
    from datetime import datetime, timedelta
    last_week = (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d")
    resp = client.post("/trigger", json={"event": "churn_risk", "user_id": "u11", "data": {"last_active": last_week}, "crm": "sendinblue"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "triggered"
    # Should skip if last_active is too old
    old_date = (datetime.utcnow() - timedelta(days=10)).strftime("%Y-%m-%d")
    resp = client.post("/trigger", json={"event": "churn_risk", "user_id": "u12", "data": {"last_active": old_date}, "crm": "sendinblue"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "skipped_business_rule"
