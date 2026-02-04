
import os
import redis
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict
from notification_router import NotificationRouter

app = FastAPI()
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
r = redis.Redis(host=redis_host, port=redis_port, db=0)
router = NotificationRouter()

class FinancialImpact(BaseModel):
    estimated_roi: float
    currency: str

class ExplainabilityNotification(BaseModel):
    event_id: str
    timestamp: str
    agent: str
    recipient_type: str  # 'client' or 'admin'
    reasoning: str
    observation: Optional[str]
    action: str
    outcome: Optional[str]
    technical_details: Optional[Dict[str, str]]
    financial_impact: Optional[FinancialImpact]
    recovery_path: Optional[str]

@app.post("/notify")
def notify(event: ExplainabilityNotification):
    # Publish to Redis event bus
    r.xadd('kiki:explainability:events', event.dict())
    # Select LLM provider and generate message
    llm_func = router.select_llm(event.dict())
    message = llm_func(event.dict())
    # Route notification to all relevant channels
    router.route(event.dict(), message)
    return {"status": "ok"}

@app.get("/events")
def get_events():
    # Return last 10 explainability events
    events = r.xrevrange('kiki:explainability:events', count=10)
    return [dict(e[1]) for e in events]


@app.get("/healthz")
def healthz():
	return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
