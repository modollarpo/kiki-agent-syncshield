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
import logging
from .audit_client import log_audit_event
from .syncvalue_client import predict_ltv
from .audit_log import router as audit_log_router
from .ltv_proxy import router as ltv_proxy_router
from .synctwin_proxy import router as synctwin_router


app = FastAPI(title="SyncPortal", version="1.0.0")
app.include_router(audit_log_router)
app.include_router(ltv_proxy_router)
app.include_router(synctwin_router)


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
from fastapi import HTTPException

def impact_audit(data: ImpactAuditRequest) -> ImpactAuditResponse:
    try:
        # 1. Log inbound request to SyncShield
        log_audit_event(
            event_type="impact_audit_request",
            payload={"monthly_customers": data.monthly_customers, "ltv": data.ltv, "churn": data.churn},
        )

        # 2. Try ML uplift prediction via SyncValue
        ml_result = predict_ltv(data.monthly_customers, data.ltv, data.churn)
        if ml_result and "projected_uplift" in ml_result:
            projected_uplift = ml_result["projected_uplift"]
            conservative_uplift = ml_result.get("conservative_uplift", projected_uplift * 0.8)
            aggressive_uplift = ml_result.get("aggressive_uplift", projected_uplift * 1.2)
        else:
            # Fallback: local stub logic
            conservative_lift = float(os.getenv("IMPACT_AUDIT_CONSERVATIVE_LIFT", "0.15"))
            aggressive_lift = float(os.getenv("IMPACT_AUDIT_AGGRESSIVE_LIFT", "0.30"))
            churn_factor = 1 - (data.churn / 100)
            conservative_uplift = data.monthly_customers * data.ltv * conservative_lift * churn_factor
            aggressive_uplift = data.monthly_customers * data.ltv * aggressive_lift * churn_factor
            avg_lift = (conservative_lift + aggressive_lift) / 2
            projected_uplift = data.monthly_customers * data.ltv * avg_lift * churn_factor

        fee_pct = float(os.getenv("KIKI_PERFORMANCE_FEE_PCT", "0.20"))
        kiki_performance_fee = projected_uplift * fee_pct
        client_net_profit = projected_uplift - kiki_performance_fee
        prospect_id = str(uuid.uuid4())

        # 3. Log outbound response to SyncShield
        log_audit_event(
            event_type="impact_audit_response",
            payload={
                "projected_uplift": projected_uplift,
                "kiki_performance_fee": kiki_performance_fee,
                "client_net_profit": client_net_profit,
                "conservative_uplift": conservative_uplift,
                "aggressive_uplift": aggressive_uplift,
                "prospect_id": prospect_id,
            },
        )

        return ImpactAuditResponse(
            projected_uplift=projected_uplift,
            kiki_performance_fee=kiki_performance_fee,
            client_net_profit=client_net_profit,
            conservative_uplift=conservative_uplift,
            aggressive_uplift=aggressive_uplift,
            prospect_id=prospect_id,
        )
    except Exception as e:
        logging.exception("/impact_audit failed")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
