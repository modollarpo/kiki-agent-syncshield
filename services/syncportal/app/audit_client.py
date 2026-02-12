"""Audit logging client for SyncShield integration (FastAPI).
"""
import os
import httpx
import logging
from typing import Optional

def log_audit_event(event_type: str, payload: dict) -> Optional[dict]:
    """
    Sends an audit event to SyncShield's /audit endpoint.
    """
    syncshield_url = os.getenv("SYNCSHIELD_AUDIT_URL", "http://syncshield:8080/audit")
    try:
        data = {
            "event_type": event_type,
            "payload": payload,
        }
        resp = httpx.post(syncshield_url, json=data, timeout=2)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logging.warning(f"Audit log failed: {e}")
        return None
