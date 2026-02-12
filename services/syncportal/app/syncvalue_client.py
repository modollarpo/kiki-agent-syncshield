"""SyncValue ML model client for uplift/LTV prediction (FastAPI).
"""
import os
import httpx
import logging
from typing import Optional

def predict_ltv(monthly_customers: int, ltv: float, churn: float) -> Optional[dict]:
    """
    Calls SyncValue's /predict-ltv endpoint for uplift prediction.
    """
    syncvalue_url = os.getenv("SYNCVALUE_LTV_URL", "http://syncvalue:8000/predict-ltv")
    try:
        req = {
            "monthly_customers": monthly_customers,
            "ltv": ltv,
            "churn": churn,
        }
        resp = httpx.post(syncvalue_url, json=req, timeout=2)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logging.warning(f"SyncValue LTV call failed: {e}")
        return None
