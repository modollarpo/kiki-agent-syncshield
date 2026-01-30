"""
Configuration loader for Acquisition Agent
- Loads environment variables and config files
- Supports adapter selection and audit log path
"""
import os

class Config:
    ADAPTER = os.getenv("ADAPTER", "MockAdapter")
    META_API_KEY = os.getenv("META_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "acquisition_audit.log")
