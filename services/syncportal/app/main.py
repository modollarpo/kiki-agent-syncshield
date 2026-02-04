"""SyncPortal

Onboarding API surface used by the enterprise dashboard.
Currently provides the Impact Audit endpoint.

This service is intentionally lightweight and can later integrate:
- SyncValue for model-backed uplift prediction
- SyncShield for audit logging + compliance
"""

from __future__ import annotations

import os
import uuid

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(title="SyncPortal", version="1.0.0")


class ImpactAuditRequest(BaseModel):
    monthly_customers: int = Field(..., ge=0)
    ltv: float = Field(..., ge=0)
    churn: float = Field(..., ge=0, le=100)


class ImpactAuditResponse(BaseModel):
    projected_uplift: float
    kiki_performance_fee: float
    client_net_profit: float
    conservative_uplift: float
    aggressive_uplift: float
    prospect_id: str


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/impact_audit", response_model=ImpactAuditResponse)
def impact_audit(data: ImpactAuditRequest) -> ImpactAuditResponse:
    # Stub uplift model (production-ready contract; replace with SyncValue integration)
    conservative_lift = float(os.getenv("IMPACT_AUDIT_CONSERVATIVE_LIFT", "0.15"))
    aggressive_lift = float(os.getenv("IMPACT_AUDIT_AGGRESSIVE_LIFT", "0.30"))
    fee_pct = float(os.getenv("KIKI_PERFORMANCE_FEE_PCT", "0.20"))

    churn_factor = 1 - (data.churn / 100)
    conservative_uplift = data.monthly_customers * data.ltv * conservative_lift * churn_factor
    aggressive_uplift = data.monthly_customers * data.ltv * aggressive_lift * churn_factor

    avg_lift = (conservative_lift + aggressive_lift) / 2
    projected_uplift = data.monthly_customers * data.ltv * avg_lift * churn_factor

    kiki_performance_fee = projected_uplift * fee_pct
    client_net_profit = projected_uplift - kiki_performance_fee

    return ImpactAuditResponse(
        projected_uplift=projected_uplift,
        kiki_performance_fee=kiki_performance_fee,
        client_net_profit=client_net_profit,
        conservative_uplift=conservative_uplift,
        aggressive_uplift=aggressive_uplift,
        prospect_id=str(uuid.uuid4()),
    )
