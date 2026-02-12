"""Audit log viewing utility for SyncPortal (FastAPI).
"""
import os
import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/audit_log")
def get_audit_log():
    """
    Fetches recent audit events from SyncShield's /audit/log endpoint.
    """
    syncshield_url = os.getenv("SYNCSHIELD_AUDIT_LOG_URL", "http://syncshield:8080/audit/log")
    try:
        resp = httpx.get(syncshield_url, timeout=2)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch audit log: {e}")
