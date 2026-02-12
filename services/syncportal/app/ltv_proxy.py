"""Proxy endpoint for direct ML LTV prediction (FastAPI).
"""
import os
import httpx
from fastapi import APIRouter, HTTPException, Body

router = APIRouter()

@router.post("/predict_ltv")
def predict_ltv_proxy(payload: dict = Body(...)):
    """
    Proxies LTV prediction requests to SyncValue's /predict-ltv endpoint.
    """
    syncvalue_url = os.getenv("SYNCVALUE_LTV_URL", "http://syncvalue:8000/predict-ltv")
    try:
        resp = httpx.post(syncvalue_url, json=payload, timeout=2)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to proxy LTV prediction: {e}")
