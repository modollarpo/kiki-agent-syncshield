"""SyncTwin API: Simulation and Health Endpoints (FastAPI)
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uuid
import random

app = FastAPI(title="SyncTwin", version="1.0.0")

class SimulateStrategyRequest(BaseModel):
    strategy: str = Field(...)
    budget: float = Field(..., ge=0)

class SimulateStrategyResponse(BaseModel):
    confidence_score: float
    risk_profile: str
    projected_net_profit_uplift: float
    simulation_id: str
    details: dict

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/simulate-strategy", response_model=SimulateStrategyResponse)
def simulate_strategy(req: SimulateStrategyRequest):
    # Simulate a strategy with random but plausible values
    confidence_score = round(random.uniform(0.7, 0.99), 3)
    risk_profile = random.choice(["conservative", "moderate", "aggressive"])
    projected_net_profit_uplift = round(req.budget * random.uniform(0.08, 0.35), 2)
    simulation_id = str(uuid.uuid4())
    details = {
        "strategy": req.strategy,
        "budget": req.budget,
        "simulated": True,
        "notes": "This is a mock simulation. Replace with real ML logic."
    }
    return SimulateStrategyResponse(
        confidence_score=confidence_score,
        risk_profile=risk_profile,
        projected_net_profit_uplift=projected_net_profit_uplift,
        simulation_id=simulation_id,
        details=details,
    )
