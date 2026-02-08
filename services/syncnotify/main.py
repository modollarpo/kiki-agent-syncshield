from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict
import asyncio
import logging

app = FastAPI(title="SyncNotify - Centralized Notification System")
logger = logging.getLogger(__name__)

class ReasoningMetadata(BaseModel):
    agent_id: str
    action_type: str
    confidence_score: float
    intent: str
    evidence: str
    reasoning_text: str


class BudgetAlertRequest(BaseModel):
    client_id: str
    severity: str  # "INFO", "WARNING", "CRITICAL"
    title: str
    message: str
    metadata: Optional[Dict[str, str]] = None


class BudgetAlertResponse(BaseModel):
    success: bool
    notification_id: str

async def send_to_client_portal(msg: str):
    # Placeholder: send to Slack, email, or dashboard
    print(f"[CLIENT PORTAL] {msg}")

async def send_to_admin_console(msg: str):
    # Placeholder: send to admin Slack, email, or dashboard
    print(f"[ADMIN CONSOLE] {msg}")

@app.post("/notify")
async def process_xai_event(metadata: ReasoningMetadata):
    # 1. Transform for Client (Simplified, ROI-focused)
    client_msg = f"Strategic Update: {metadata.intent} based on {metadata.evidence}."
    # 2. Transform for Admin (Detailed, Audit-focused)
    admin_msg = f"AGENT_{metadata.agent_id} | CONFIDENCE: {metadata.confidence_score} | {metadata.reasoning_text}"
    # 3. Route to proper channels (Slack, Email, or Dashboard Pulse)
    await asyncio.gather(
        send_to_client_portal(client_msg),
        send_to_admin_console(admin_msg)
    )
    return {"status": "ok"}


@app.post("/send-alert", response_model=BudgetAlertResponse)
async def send_budget_alert(request: BudgetAlertRequest) -> BudgetAlertResponse:
    """
    Send budget reallocation alerts to clients via email/SMS/Slack.
    
    Called by GlobalBudgetOptimizer when budget shifts occur.
    
    Args:
        request: Alert details (client_id, severity, title, message, metadata)
        
    Returns:
        BudgetAlertResponse with success status and notification ID
        
    Example:
        POST /send-alert
        {
            "client_id": "demo-client-001",
            "severity": "INFO",
            "title": "Budget Auto-Reallocation",
            "message": "Meta CPMs spiked (+40%). Shifted $100/day to TikTok (4.0x vs 2.5x)",
            "metadata": {
                "from_platform": "PLATFORM_META",
                "to_platform": "PLATFORM_TIKTOK",
                "amount_shifted": "100.00"
            }
        }
    """
    import uuid
    
    notification_id = f"notif-{uuid.uuid4().hex[:8]}"
    
    # Format alert message
    severity_emoji = {
        "INFO": "ℹ️",
        "WARNING": "⚠️",
        "CRITICAL": "🚨"
    }
    emoji = severity_emoji.get(request.severity, "📢")
    
    formatted_message = f"{emoji} **{request.title}**\n{request.message}"
    
    if request.metadata:
        formatted_message += "\n\nDetails:"
        for key, value in request.metadata.items():
            formatted_message += f"\n- {key}: {value}"
    
    # Log alert
    logger.info(f"[{request.severity}] {request.title} - Client: {request.client_id}")
    logger.info(f"Message: {request.message}")
    
    # TODO: Implement actual notification delivery
    # - Email via SendGrid
    # - SMS via Twilio
    # - Slack via Webhook
    # For now, just log to console
    await send_to_client_portal(formatted_message)
    
    return BudgetAlertResponse(
        success=True,
        notification_id=notification_id
    )

