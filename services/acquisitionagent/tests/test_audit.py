"""
Unit tests for Acquisition Agent audit logging
"""
import os
from infrastructure.audit import log_event, LOG_PATH

def test_log_event(tmp_path):
    test_log = tmp_path / "test_audit.log"
    os.environ["AUDIT_LOG_PATH"] = str(test_log)
    log_event("Test audit event")
    with open(test_log, "r") as f:
        lines = f.readlines()
    assert any("Test audit event" in line for line in lines)
