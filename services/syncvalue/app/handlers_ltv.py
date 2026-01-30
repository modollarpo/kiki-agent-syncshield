from fastapi import APIRouter, HTTPException
from schemas.ltv_prediction import LTVPredictionRequest, LTVPredictionResponse
from schemas.bid import BidRequest, BidResponse
import httpx
from prometheus_client import Counter
from opentelemetry import trace
from opentelemetry.trace import Span
import logging

router = APIRouter()

# Prometheus metrics for integration calls
SYNCFLOW_BID_COUNT = Counter("syncvalue_syncflow_bid_total", "Total SyncFlow bid API calls")
SYNCENGAGE_TRIGGER_COUNT = Counter("syncvalue_syncengage_trigger_total", "Total SyncEngage trigger API calls")
logger = logging.getLogger("syncvalue.handlers_ltv")
tracer = trace.get_tracer(__name__)

@router.post("/predict-ltv", response_model=LTVPredictionResponse)
def predict_ltv(req: LTVPredictionRequest):
    # Advanced logic: call SyncFlow for bid context, trace and metric
    with tracer.start_as_current_span("predict_ltv_handler") as span:
        bid_resp = call_syncflow_bid(req.user_id, span)
        ltv = 0.8 if bid_resp and getattr(bid_resp, "accepted", False) else 0.3
        # Example: trigger SyncEngage for CRM automation (integration)
        trigger_syncengage_crm(req.user_id, span)
        return LTVPredictionResponse(user_id=req.user_id, ltv=ltv)

def call_syncflow_bid(user_id: str, span: Span = None) -> BidResponse | None:
    SYNCFLOW_BID_COUNT.inc()
    try:
        req = BidRequest(user_id=user_id, ad_slot="banner_top", bid_amount=1.23)
        with tracer.start_as_current_span("call_syncflow_bid", context=trace.set_span_in_context(span)):
            resp = httpx.post("http://syncflow:8000/execute-bid", json=req.dict(), timeout=2)
            if resp.status_code == 200:
                logger.info(f"SyncFlow bid success for {user_id}")
                return BidResponse(**resp.json())
            logger.warning(f"SyncFlow bid failed for {user_id}: {resp.status_code}")
    except Exception as e:
        logger.error(f"SyncFlow bid error for {user_id}: {e}")
    return None

def trigger_syncengage_crm(user_id: str, span: Span = None):
    SYNCENGAGE_TRIGGER_COUNT.inc()
    try:
        # Example: trigger CRM automation in SyncEngage
        payload = {"user_id": user_id, "event": "ltv_prediction"}
        with tracer.start_as_current_span("trigger_syncengage_crm", context=trace.set_span_in_context(span)):
            resp = httpx.post("http://syncengage:8000/trigger-crm", json=payload, timeout=2)
            if resp.status_code == 200:
                logger.info(f"SyncEngage CRM triggered for {user_id}")
            else:
                logger.warning(f"SyncEngage CRM trigger failed for {user_id}: {resp.status_code}")
    except Exception as e:
        logger.error(f"SyncEngage CRM error for {user_id}: {e}")
