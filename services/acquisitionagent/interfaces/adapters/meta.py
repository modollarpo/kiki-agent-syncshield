"""
Meta (Facebook/Instagram) ad platform adapter (abstract)
- Subclass of AdPlatformAdapter
- All external calls are stubbed/mocked
"""
from .base import AdPlatformAdapter
from typing import Dict, Any

class MetaAdapter(AdPlatformAdapter):
    def optimise_spend(self, allocation: Dict[str, float], config: Dict[str, Any]) -> Dict[str, Any]:
        # Stubbed: In production, call Meta API
        return {"status": "success", "details": allocation}

    def fetch_performance(self, campaign_ids: list[str], config: Dict[str, Any]) -> Dict[str, Any]:
        # Stubbed: In production, call Meta API
        return {cid: {"impressions": 1000, "clicks": 50} for cid in campaign_ids}
