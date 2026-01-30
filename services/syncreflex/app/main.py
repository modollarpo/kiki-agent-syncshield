"""
SyncReflex – Real-Time Feedback Loop
"""
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, Any
import uuid

app = FastAPI(title="SyncReflex Attribution Listener")

# In-memory store for creative performance
performance_store: Dict[str, Dict[str, Any]] = {}

class AttributionEvent(BaseModel):
    creative_id: str
    ctr: float
    conversions: int
    platform: str
    style: str

@app.post("/attribution")
async def ingest_attribution(event: AttributionEvent):
    performance_store[event.creative_id] = {
        "ctr": event.ctr,
        "conversions": event.conversions,
        "platform": event.platform,
        "style": event.style
    }
    # If CTR/conversions are low, send negative weight signal (stub)
    if event.ctr < 0.01 or event.conversions == 0:
        # In production, call SyncCreate/PromptEngineer via REST/gRPC
        return {"action": "negative_weight", "creative_id": event.creative_id}
    return {"action": "positive_weight", "creative_id": event.creative_id}

@app.get("/performance/{creative_id}")
async def get_performance(creative_id: str):
    return performance_store.get(creative_id, {})

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
