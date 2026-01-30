"""
Unit tests for Acquisition Agent config loader
"""
import os
from app.config import Config

def test_config_defaults():
    assert Config.ADAPTER == "MockAdapter"
    assert Config.AUDIT_LOG_PATH == "acquisition_audit.log"

def test_config_env(monkeypatch):
    monkeypatch.setenv("ADAPTER", "MetaAdapter")
    monkeypatch.setenv("AUDIT_LOG_PATH", "/tmp/test.log")
    assert Config.ADAPTER == "MetaAdapter"
    assert Config.AUDIT_LOG_PATH == "/tmp/test.log"
