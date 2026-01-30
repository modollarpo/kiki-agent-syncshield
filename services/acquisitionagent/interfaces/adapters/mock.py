"""
Mock adapter for testing and local development
- Subclass of AdPlatformAdapter
"""
from .base import AdPlatformAdapter
from typing import Dict, Any

class MockAdapter(AdPlatformAdapter):
    def optimise_spend(self, allocation: Dict[str, float], config: Dict[str, Any]) -> Dict[str, Any]:
        # No-op, just echo allocation
        return {"status": "mocked", "details": allocation}

    def fetch_performance(self, campaign_ids: list[str], config: Dict[str, Any]) -> Dict[str, Any]:
        # Return dummy data
        return {cid: {"impressions": 500, "clicks": 25} for cid in campaign_ids}
