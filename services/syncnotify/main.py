from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import asyncio

app = FastAPI()

class ReasoningMetadata(BaseModel):
    agent_id: str
    action_type: str
    confidence_score: float
    intent: str
    evidence: str
    reasoning_text: str

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
