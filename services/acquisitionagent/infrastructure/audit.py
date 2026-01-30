"""
Audit logging for Acquisition Agent
- All optimisation and execution events are logged
- Supports file and stdout logging
"""
import logging
import os

LOG_PATH = os.getenv("AUDIT_LOG_PATH", "acquisition_audit.log")

logger = logging.getLogger("acquisition_audit")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOG_PATH)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def log_event(event: str):
    logger.info(event)
