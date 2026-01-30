"""
Acquisition Agent Service Entry Point
- FastAPI app
- Event-driven endpoints
- Consumes SyncValue™ predictions
- Clean separation of decision logic and execution adapters
"""
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from domain.optimisation import optimise_budget, SimulationRequest, SimulationResult
from infrastructure.event import publish_event
from infrastructure.audit import log_event
from interfaces.syncvalue import get_ltv_predictions
from app.config import Config
from interfaces.adapters.base import AdPlatformAdapter
from interfaces.adapters.meta import MetaAdapter
from interfaces.adapters.google import GoogleAdapter
from interfaces.adapters.mock import MockAdapter

app = FastAPI(title="Acquisition Agent Service")

# Adapter selection
ADAPTERS = {
    "MetaAdapter": MetaAdapter(),
    "GoogleAdapter": GoogleAdapter(),
    "MockAdapter": MockAdapter(),
}
adapter: AdPlatformAdapter = ADAPTERS.get(Config.ADAPTER, MockAdapter())

class OptimiseRequest(BaseModel):
    campaigns: list[str]
    budget: float
    constraints: dict
    pacing: dict

class OptimiseResult(BaseModel):
    allocation: dict
    predicted_ltv: dict
    events: list[str]

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/optimise", response_model=OptimiseResult)
def optimise(request: OptimiseRequest):
    # Get LTV predictions from SyncValue (abstracted)
    ltv = get_ltv_predictions(request.campaigns)
    # Optimise budget allocation
    allocation, events = optimise_budget(
        campaigns=request.campaigns,
        budget=request.budget,
        constraints=request.constraints,
        pacing=request.pacing,
        ltv_predictions=ltv
    )
    # Execute allocation via selected adapter (abstracted)
    adapter_result = adapter.optimise_spend(allocation, config={})
    # Audit log all events and adapter results
    for event in events:
        publish_event(event)
        log_event(event)
    log_event(f"Adapter result: {adapter_result}")
    return OptimiseResult(allocation=allocation, predicted_ltv=ltv, events=events)

@app.post("/simulate", response_model=SimulationResult)
def simulate(request: SimulationRequest):
    # Run scenario simulation (what-if analysis)
    result = SimulationResult.simulate(request)
    return result
