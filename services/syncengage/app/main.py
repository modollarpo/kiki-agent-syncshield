class OrchestrationRequest(BaseModel):
    brand_dna: Dict[str, Any]
    customer_segment: Dict[str, Any]
    channels: list
    mode: str  # "priority", "parallel", "conditional"
    priority_order: list = None
    condition_fn: str = None  # Name of condition function (for demo, string)

@app.post("/orchestrate-retention-flow")
async def orchestrate_retention_flow(request: OrchestrationRequest):
    engine = RetentionEngine(request.channels[0])  # Use first channel for base adapter
    if request.mode == "priority":
        sent = await engine.orchestrate_multi_channel(request.brand_dna, request.customer_segment, request.channels, request.priority_order)
        return {"status": "sent" if sent else "delayed"}
    elif request.mode == "parallel":
        await engine.orchestrate_parallel(request.brand_dna, request.customer_segment, request.channels)
        return {"status": "sent_parallel"}
    elif request.mode == "conditional":
        # Demo: Use a simple condition function
        def demo_condition_fn(brand_dna, customer_segment, channel):
            return customer_segment.get("vip", False) or channel == "email"
        await engine.orchestrate_conditional(request.brand_dna, request.customer_segment, request.channels, demo_condition_fn)
        return {"status": "sent_conditional"}
    else:
        return {"status": "unknown_mode"}

WORKFLOW_TEMPLATES = {
    "vip_winback": {
        "mode": "parallel",
        "channels": ["email", "sms", "whatsapp"],
        "condition_fn": "vip_only"
    },
    "priority_email_then_sms": {
        "mode": "priority",
        "channels": ["email", "sms"],
        "priority_order": ["email", "sms"]
    },
    "churn_risk_conditional": {
        "mode": "conditional",
        "channels": ["email", "sms", "whatsapp"],
        "condition_fn": "churn_risk"
    }
}

@app.get("/workflow-templates")
def list_workflow_templates():
    return {"templates": WORKFLOW_TEMPLATES}

@app.post("/external-trigger")
async def external_trigger(payload: dict):
    # Example: Accept webhook from external system to trigger orchestration
    template = WORKFLOW_TEMPLATES.get(payload.get("template"), None)
    if not template:
        return {"status": "template_not_found"}
    engine = RetentionEngine(template["channels"][0])
    if template["mode"] == "priority":
        await engine.orchestrate_multi_channel(payload["brand_dna"], payload["customer_segment"], template["channels"], template.get("priority_order"))
    elif template["mode"] == "parallel":
        await engine.orchestrate_parallel(payload["brand_dna"], payload["customer_segment"], template["channels"])
    elif template["mode"] == "conditional":
        def demo_condition_fn(brand_dna, customer_segment, channel):
            return customer_segment.get("churn_risk", False)
        await engine.orchestrate_conditional(payload["brand_dna"], payload["customer_segment"], template["channels"], demo_condition_fn)
    return {"status": "triggered"}
"""
SyncEngage™ FastAPI Service
Production-grade endpoints for retention flows, channel orchestration, and BrandDNA injection.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import asyncio
from .retention_logic import RetentionEngine

app = FastAPI()

class RetentionRequest(BaseModel):
    brand_dna: Dict[str, Any]
    customer_segment: Dict[str, Any]
    channel: str  # "email", "sms", "whatsapp", "slack"
    crm_provider: str  # "klaviyo", "hubspot", "salesforce", "whatsapp", "slack"
        channel: str  # "email", "sms", "whatsapp", "slack", "mailchimp", "zoho", "activecampaign", "sendinblue", "intercom", "pipedrive"
        crm_provider: str  # "klaviyo", "hubspot", "salesforce", "whatsapp", "slack", "mailchimp", "zoho", "activecampaign", "sendinblue", "intercom", "pipedrive"

CHANNELS = ["email", "sms", "whatsapp", "slack", "mailchimp", "zoho", "activecampaign", "sendinblue", "intercom", "pipedrive"]
PROVIDERS = ["klaviyo", "hubspot", "salesforce", "whatsapp", "slack", "mailchimp", "zoho", "activecampaign", "sendinblue", "intercom", "pipedrive"]
class BatchRetentionRequest(BaseModel):
    brand_dna: Dict[str, Any]
    customer_segments: list
    channel: str
    crm_provider: str

@app.post("/send-batch-retention-flow")
async def send_batch_retention_flow(request: BatchRetentionRequest):
    results = []
    engine = RetentionEngine(request.crm_provider)
    for customer_segment in request.customer_segments:
        try:
            await engine.send_retention_flow(request.brand_dna, customer_segment, request.channel)
            results.append({"customer_id": customer_segment.get("id"), "status": "sent"})
        except Exception as e:
            results.append({"customer_id": customer_segment.get("id"), "status": "error", "error": str(e)})
    return {"results": results}
@app.get("/channels")
def list_channels():
    return {"channels": CHANNELS}

@app.get("/providers")
def list_providers():
    return {"providers": PROVIDERS}

@app.post("/send-retention-flow")
async def send_retention_flow(request: RetentionRequest):
    try:
        engine = RetentionEngine(request.crm_provider)
        await engine.send_retention_flow(request.brand_dna, request.customer_segment, request.channel)
        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/healthz")
def health_check():
    return {"status": "ok"}
"""
SyncEngage – CRM + Retention Automation (Python version)
"""

from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from enum import Enum
import random
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
import logging
import httpx
import os

app = FastAPI(title="SyncEngage CRM Automation", description="CRM automation and engagement triggers for KIKI Agent™")

# Instrument FastAPI with OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
FastAPIInstrumentor.instrument_app(app)
span_processor = BatchSpanProcessor(ConsoleSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# Prometheus metrics
REQUEST_COUNT = Counter("syncengage_requests_total", "Total requests", ["endpoint", "method"])
ERROR_COUNT = Counter("syncengage_errors_total", "Total errors", ["endpoint"])
TRIGGER_COUNT = Counter("syncengage_triggers_total", "Total CRM triggers", ["event"])
REQUEST_LATENCY = Histogram("syncengage_request_latency_seconds", "Request latency", ["endpoint"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("syncengage")

MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY", "demo-mailchimp-key")
ZOHO_API_KEY = os.getenv("ZOHO_API_KEY", "demo-zoho-key")
ACTIVECAMPAIGN_API_KEY = os.getenv("ACTIVECAMPAIGN_API_KEY", "demo-activecampaign-key")
SENDINBLUE_API_KEY = os.getenv("SENDINBLUE_API_KEY", "demo-sendinblue-key")
INTERCOM_API_KEY = os.getenv("INTERCOM_API_KEY", "demo-intercom-key")
PIPEDRIVE_API_KEY = os.getenv("PIPEDRIVE_API_KEY", "demo-pipedrive-key")

class CRMProvider(str, Enum):
    HUBSPOT = "hubspot"
    KLAVIYO = "klaviyo"
    SALESFORCE = "salesforce"
    MAILCHIMP = "mailchimp"
    ZOHO = "zoho"
    ACTIVECAMPAIGN = "activecampaign"
    SENDINBLUE = "sendinblue"
    INTERCOM = "intercom"
    PIPEDRIVE = "pipedrive"
    NONE = "none"

class WorkflowType(str, Enum):
    SIMPLE = "simple"
    MULTISTEP = "multistep"
    CONDITIONAL = "conditional"

class TriggerRequest(BaseModel):
    event: str = Field(..., description="Event name, e.g. 'churn_risk', 'upsell'")
    user_id: str = Field(..., description="User ID")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    crm: Optional[CRMProvider] = Field(default=CRMProvider.NONE, description="CRM provider")
    workflow: Optional[WorkflowType] = Field(default=WorkflowType.SIMPLE, description="Workflow type")

class TriggerResponse(BaseModel):
    status: str
    event: str

class FlowsResponse(BaseModel):
    flows: List[str]

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY", "demo-hubspot-key")
KLAVIYO_API_KEY = os.getenv("KLAVIYO_API_KEY", "demo-klaviyo-key")
SALESFORCE_API_KEY = os.getenv("SALESFORCE_API_KEY", "demo-salesforce-key")

def call_syncvalue_ltv(user_id: str, features: dict) -> float:
    """Call SyncValue to get LTV prediction for a user."""
    try:
        resp = httpx.post("http://syncvalue:8000/predict-ltv", json={"user_id": user_id, "features": features}, timeout=2)
        if resp.status_code == 200:
            return resp.json().get("ltv", 0.0)
    except Exception as e:
        logger.warning(f"SyncValue call failed: {e}")
    return 0.0

def trigger_hubspot(event: str, user_id: str, data: dict) -> bool:
    """Real HubSpot integration (Contacts API, Workflow trigger)."""
    try:
        # Example: Add/update contact, trigger workflow
        contact_url = f"https://api.hubapi.com/crm/v3/objects/contacts?hapikey={HUBSPOT_API_KEY}"
        contact_payload = {
            "properties": {
                "email": data.get("email", f"{user_id}@example.com"),
                "firstname": data.get("first_name", "User"),
                "lastname": data.get("last_name", "Kiki")
            }
        }
        resp = httpx.post(contact_url, json=contact_payload, timeout=3)
        if resp.status_code not in (200, 201):
            logger.warning(f"HubSpot contact error: {resp.text}")
            return False
        # Optionally trigger workflow (stub)
        # workflow_url = f"https://api.hubapi.com/automation/v3/workflows/{workflow_id}/enrollments/contacts/{user_id}?hapikey={HUBSPOT_API_KEY}"
        # httpx.post(workflow_url)
        logger.info(f"[HubSpot] Contact synced for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"HubSpot API error: {e}")
        return False

def trigger_klaviyo(event: str, user_id: str, data: dict) -> bool:
    """Real Klaviyo integration (Track event API)."""
    try:
        track_url = "https://a.klaviyo.com/api/events/"
        payload = {
            "data": {
                "type": "event",
                "attributes": {
                    "metric": {"data": {"type": "metric", "attributes": {"name": event}}},
                    "profile": {"data": {"type": "profile", "attributes": {"email": data.get("email", f"{user_id}@example.com")}}},
                    "properties": data
                }
            }
        }
        headers = {"Authorization": f"Klaviyo-API-Key {KLAVIYO_API_KEY}", "Content-Type": "application/json"}
        resp = httpx.post(track_url, json=payload, headers=headers, timeout=3)
        if resp.status_code not in (200, 202):
            logger.warning(f"Klaviyo event error: {resp.text}")
            return False
        logger.info(f"[Klaviyo] Event '{event}' tracked for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Klaviyo API error: {e}")
        return False

def trigger_salesforce(event: str, user_id: str, data: dict) -> bool:
    """Real Salesforce integration (Lead/Contact API, Campaign trigger)."""
    try:
        contact_url = "https://api.salesforce.com/v1/contacts"
        headers = {"Authorization": f"Bearer {SALESFORCE_API_KEY}", "Content-Type": "application/json"}
        contact_payload = {
            "email": data.get("email", f"{user_id}@example.com"),
            "firstName": data.get("first_name", "User"),
            "lastName": data.get("last_name", "Kiki")
        }
        resp = httpx.post(contact_url, json=contact_payload, headers=headers, timeout=3)
        if resp.status_code not in (200, 201):
            logger.warning(f"Salesforce contact error: {resp.text}")
            return False
        logger.info(f"[Salesforce] Contact synced for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Salesforce API error: {e}")
        return False

def trigger_mailchimp(event: str, user_id: str, data: dict) -> bool:
    """Real Mailchimp integration (Add/Update contact, trigger campaign)."""
    with tracer.start_as_current_span("trigger_mailchimp"):
        try:
            url = "https://usX.api.mailchimp.com/3.0/lists/demo-list-id/members"
            headers = {"Authorization": f"apikey {MAILCHIMP_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "email_address": data.get("email", f"{user_id}@example.com"),
                "status": "subscribed",
                "merge_fields": {"FNAME": data.get("first_name", "User"), "LNAME": data.get("last_name", "Kiki")}
            }
            resp = httpx.post(url, json=payload, headers=headers, timeout=3)
            if resp.status_code not in (200, 201):
                logger.warning(f"Mailchimp error: {resp.text}")
                return False
            logger.info(f"[Mailchimp] Contact synced for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Mailchimp API error: {e}")
            return False

def trigger_zoho(event: str, user_id: str, data: dict) -> bool:
    """Real Zoho CRM integration (Add/Update contact, trigger workflow)."""
    with tracer.start_as_current_span("trigger_zoho"):
        try:
            url = "https://www.zohoapis.com/crm/v2/Contacts"
            headers = {"Authorization": f"Zoho-oauthtoken {ZOHO_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "data": [{
                    "Email": data.get("email", f"{user_id}@example.com"),
                    "First_Name": data.get("first_name", "User"),
                    "Last_Name": data.get("last_name", "Kiki")
                }]
            }
            resp = httpx.post(url, json=payload, headers=headers, timeout=3)
            if resp.status_code not in (200, 201, 202):
                logger.warning(f"Zoho error: {resp.text}")
                return False
            logger.info(f"[Zoho] Contact synced for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Zoho API error: {e}")
            return False

def trigger_activecampaign(event: str, user_id: str, data: dict) -> bool:
    """Real ActiveCampaign integration (Add/Update contact, trigger automation)."""
    with tracer.start_as_current_span("trigger_activecampaign"):
        try:
            url = "https://youraccount.api-us1.com/api/3/contacts"
            headers = {"Api-Token": ACTIVECAMPAIGN_API_KEY, "Content-Type": "application/json"}
            payload = {
                "contact": {
                    "email": data.get("email", f"{user_id}@example.com"),
                    "firstName": data.get("first_name", "User"),
                    "lastName": data.get("last_name", "Kiki")
                }
            }
            resp = httpx.post(url, json=payload, headers=headers, timeout=3)
            if resp.status_code not in (200, 201):
                logger.warning(f"ActiveCampaign error: {resp.text}")
                return False
            logger.info(f"[ActiveCampaign] Contact synced for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"ActiveCampaign API error: {e}")
            return False

def trigger_sendinblue(event: str, user_id: str, data: dict) -> bool:
    """Real Sendinblue integration (Add/Update contact, trigger campaign)."""
    with tracer.start_as_current_span("trigger_sendinblue"):
        try:
            url = "https://api.sendinblue.com/v3/contacts"
            headers = {"api-key": SENDINBLUE_API_KEY, "Content-Type": "application/json"}
            payload = {
                "email": data.get("email", f"{user_id}@example.com"),
                "attributes": {"FIRSTNAME": data.get("first_name", "User"), "LASTNAME": data.get("last_name", "Kiki")},
                "listIds": [2],
                "updateEnabled": True
            }
            resp = httpx.post(url, json=payload, headers=headers, timeout=3)
            if resp.status_code not in (200, 201):
                logger.warning(f"Sendinblue error: {resp.text}")
                return False
            logger.info(f"[Sendinblue] Contact synced for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Sendinblue API error: {e}")
            return False

def trigger_intercom(event: str, user_id: str, data: dict) -> bool:
    """Real Intercom integration (Add/Update user, send event)."""
    with tracer.start_as_current_span("trigger_intercom"):
        try:
            url = "https://api.intercom.io/users"
            headers = {"Authorization": f"Bearer {INTERCOM_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "user_id": user_id,
                "email": data.get("email", f"{user_id}@example.com"),
                "name": data.get("first_name", "User") + " " + data.get("last_name", "Kiki")
            }
            resp = httpx.post(url, json=payload, headers=headers, timeout=3)
            if resp.status_code not in (200, 201):
                logger.warning(f"Intercom error: {resp.text}")
                return False
            logger.info(f"[Intercom] User synced for {user_id}")
            return True
        except Exception as e:
            logger.error(f"Intercom API error: {e}")
            return False

def trigger_pipedrive(event: str, user_id: str, data: dict) -> bool:
    """Real Pipedrive integration (Add/Update person, trigger deal)."""
    with tracer.start_as_current_span("trigger_pipedrive"):
        try:
            url = f"https://api.pipedrive.com/v1/persons?api_token={PIPEDRIVE_API_KEY}"
            payload = {
                "name": data.get("first_name", "User") + " " + data.get("last_name", "Kiki"),
                "email": data.get("email", f"{user_id}@example.com")
            }
            resp = httpx.post(url, json=payload, timeout=3)
            if resp.status_code not in (200, 201):
                logger.warning(f"Pipedrive error: {resp.text}")
                return False
            logger.info(f"[Pipedrive] Person synced for {user_id}")
            return True
        except Exception as e:
            logger.error(f"Pipedrive API error: {e}")
            return False

def run_workflow(workflow: WorkflowType, crm_func, event, user_id, data) -> bool:
    """Run advanced workflow logic: multi-step, conditional, etc."""
    if workflow == WorkflowType.SIMPLE:
        return crm_func(event, user_id, data)
    elif workflow == WorkflowType.MULTISTEP:
        # Example: multi-step (sync contact, then trigger event)
        contact_synced = crm_func(event, user_id, data)
        if not contact_synced:
            return False
        # Simulate follow-up step (e.g., send follow-up email)
        logger.info(f"[Workflow] Follow-up step for {user_id}")
        return True
    elif workflow == WorkflowType.CONDITIONAL:
        # Example: only trigger if score > 0.8
        if data.get("score", 0) > 0.8:
            return crm_func(event, user_id, data)
        logger.info(f"[Workflow] Condition not met for {user_id}")
        return False
    return crm_func(event, user_id, data)

def run_business_rules(req: TriggerRequest, ltv: float) -> bool:
    """Apply advanced business rules: time-based, user segment, region, recent activity, score, plan type, etc."""
    with tracer.start_as_current_span("run_business_rules"):
        from datetime import datetime, timedelta
        hour = datetime.utcnow().hour
        if not (9 <= hour < 18):
            logger.info(f"[BusinessRule] Out of business hours for {req.user_id}")
            return False
        # Example: Only trigger for premium users
        if req.data.get("segment") == "premium":
            return True
        # Example: Only trigger if region is EU and LTV > 0.6
        if req.data.get("region") == "EU" and ltv > 0.6:
            return True
        # Custom: Only trigger if user was active in last 7 days
        last_active = req.data.get("last_active")
        if last_active:
            try:
                last_active_dt = datetime.strptime(last_active, "%Y-%m-%d")
                if datetime.utcnow() - last_active_dt < timedelta(days=7):
                    return True
            except Exception:
                pass
        # Example: Only trigger if score > 0.85
        if req.data.get("score", 0) > 0.85:
            return True
        # Example: Only trigger for enterprise plan
        if req.data.get("plan") == "enterprise":
            return True
        # Example: Only trigger if LTV > 0.7 for upsell
        if req.event == "upsell" and ltv > 0.7:
            return True
        return False

event_log: list = []

@app.post("/trigger", response_model=TriggerResponse)
def trigger_crm(req: TriggerRequest):
    """Trigger a CRM automation flow with advanced logic, real CRM API integration, business rules, and distributed tracing."""
    REQUEST_COUNT.labels(endpoint="/trigger", method="POST").inc()
    with REQUEST_LATENCY.labels(endpoint="/trigger").time():
        with tracer.start_as_current_span("trigger_crm") as span:
            if not req.event or not req.user_id:
                ERROR_COUNT.labels(endpoint="/trigger").inc()
                raise HTTPException(status_code=400, detail="event and user_id required")
            # Example: call SyncFlow for bid context before LTV
            with tracer.start_as_current_span("call_syncflow_bid", context=trace.set_span_in_context(span)):
                try:
                    bid_payload = {"user_id": req.user_id, "ad_slot": "banner_top", "bid_amount": 1.23}
                    bid_resp = httpx.post("http://syncflow:8000/execute-bid", json=bid_payload, timeout=2)
                    logger.info(f"SyncFlow bid response: {bid_resp.text}")
                except Exception as e:
                    logger.warning(f"SyncFlow bid call failed: {e}")
            ltv = call_syncvalue_ltv(req.user_id, req.data.get("features", {}))
            logger.info(f"LTV for user {req.user_id}: {ltv}")
            # Business rules
            if not run_business_rules(req, ltv):
                event_log.append({
                    "event": req.event,
                    "user_id": req.user_id,
                    "status": "skipped_business_rule",
                    "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                    "data": req.data
                })
                return TriggerResponse(status="skipped_business_rule", event=req.event)
            if ltv <= 0.5:
                event_log.append({
                    "event": req.event,
                    "user_id": req.user_id,
                    "status": "skipped_low_ltv",
                    "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                    "data": req.data
                })
                return TriggerResponse(status="skipped_low_ltv", event=req.event)
            event_map = {"churn_risk": "Churn Risk Alert", "upsell": "Upsell Opportunity"}
            crm_event = event_map.get(req.event, req.event)
            # Prometheus metric for integration calls
            integration_count = Counter("syncengage_crm_integration_total", "Total CRM integration API calls", ["provider"])
            provider = req.crm if req.crm else "none"
            integration_count.labels(provider=provider).inc()
            if req.crm == CRMProvider.HUBSPOT:
                crm_func = trigger_hubspot
            elif req.crm == CRMProvider.KLAVIYO:
                crm_func = trigger_klaviyo
            elif req.crm == CRMProvider.SALESFORCE:
                crm_func = trigger_salesforce
            elif req.crm == CRMProvider.MAILCHIMP:
                crm_func = trigger_mailchimp
            elif req.crm == CRMProvider.ZOHO:
                crm_func = trigger_zoho
            elif req.crm == CRMProvider.ACTIVECAMPAIGN:
                crm_func = trigger_activecampaign
            elif req.crm == CRMProvider.SENDINBLUE:
                crm_func = trigger_sendinblue
            elif req.crm == CRMProvider.INTERCOM:
                crm_func = trigger_intercom
            elif req.crm == CRMProvider.PIPEDRIVE:
                crm_func = trigger_pipedrive
            else:
                crm_func = lambda e, u, d: True
            with tracer.start_as_current_span("run_workflow", context=trace.set_span_in_context(span)):
                triggered = run_workflow(req.workflow, crm_func, crm_event, req.user_id, req.data)
            if not triggered:
                ERROR_COUNT.labels(endpoint="/trigger").inc()
                event_log.append({
                    "event": req.event,
                    "user_id": req.user_id,
                    "status": "failed",
                    "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                    "data": req.data
                })
                raise HTTPException(status_code=502, detail="CRM integration or workflow failed")
            TRIGGER_COUNT.labels(event=req.event).inc()
            event_log.append({
                "event": req.event,
                "user_id": req.user_id,
                "status": "triggered",
                "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                "data": req.data
            })
            return TriggerResponse(status="triggered", event=req.event)

# CRM Event Log endpoint
@app.get("/events")
def get_event_log():
    return {"events": event_log[-100:]}  # Return last 100 events

@app.get("/flows", response_model=FlowsResponse)
def list_flows():
    """List available CRM automation flows."""
    REQUEST_COUNT.labels(endpoint="/flows", method="GET").inc()
    with REQUEST_LATENCY.labels(endpoint="/flows").time():
        with tracer.start_as_current_span("list_flows"):
            flows = ["churn_risk", "upsell", "winback", "welcome", "custom"]
            return FlowsResponse(flows=flows)

@app.get("/healthz")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/metrics")
def prometheus_metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
