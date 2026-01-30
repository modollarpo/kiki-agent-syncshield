"""
Google Ads platform adapter (abstract)
- Subclass of AdPlatformAdapter
- All external calls are stubbed/mocked
"""
from .base import AdPlatformAdapter
from typing import Dict, Any

class GoogleAdapter(AdPlatformAdapter):
    def optimise_spend(self, allocation: Dict[str, float], config: Dict[str, Any]) -> Dict[str, Any]:
        # Stubbed: In production, call Google Ads API
        return {"status": "success", "details": allocation}

    def fetch_performance(self, campaign_ids: list[str], config: Dict[str, Any]) -> Dict[str, Any]:
        # Stubbed: In production, call Google Ads API
        return {cid: {"impressions": 2000, "clicks": 100} for cid in campaign_ids}
