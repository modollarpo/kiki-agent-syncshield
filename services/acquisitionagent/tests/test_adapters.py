"""
Unit tests for Acquisition Agent ad platform adapters
- All external calls are mocked
"""
import pytest
from interfaces.adapters.base import AdPlatformAdapter
from interfaces.adapters.meta import MetaAdapter
from interfaces.adapters.google import GoogleAdapter
from interfaces.adapters.mock import MockAdapter

@pytest.mark.parametrize("adapter_cls", [MetaAdapter, GoogleAdapter, MockAdapter])
def test_adapter_optimise_spend(adapter_cls):
    adapter: AdPlatformAdapter = adapter_cls()
    allocation = {"A": 100.0, "B": 200.0}
    result = adapter.optimise_spend(allocation, config={})
    assert "status" in result
    assert "details" in result

@pytest.mark.parametrize("adapter_cls", [MetaAdapter, GoogleAdapter, MockAdapter])
def test_adapter_fetch_performance(adapter_cls):
    adapter: AdPlatformAdapter = adapter_cls()
    campaign_ids = ["A", "B"]
    result = adapter.fetch_performance(campaign_ids, config={})
    assert all(cid in result for cid in campaign_ids)
