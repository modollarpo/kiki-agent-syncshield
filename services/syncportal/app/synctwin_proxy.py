"""Proxy endpoint for SyncTwin simulation and health (FastAPI).
"""
import os
import httpx
from fastapi import APIRouter, HTTPException, Body

router = APIRouter()

@router.post("/simulate_strategy")
def simulate_strategy_proxy(payload: dict = Body(...)):
    """
    Proxies simulation requests to SyncTwin's /simulate-strategy endpoint.
    """
    synctwin_url = os.getenv("SYNCTWIN_SIM_URL", "http://synctwin:8007/simulate-strategy")
    try:
        resp = httpx.post(synctwin_url, json=payload, timeout=3)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to proxy SyncTwin simulation: {e}")

@router.get("/synctwin_health")
def synctwin_health():
    synctwin_url = os.getenv("SYNCTWIN_HEALTH_URL", "http://synctwin:8007/healthz")
    try:
        resp = httpx.get(synctwin_url, timeout=2)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to reach SyncTwin: {e}")
