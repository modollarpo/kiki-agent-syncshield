"""
Base adapter interface for ad platform integration
- All real integrations must subclass this
- All methods are abstract and must be implemented
"""
from typing import Dict, Any

class AdPlatformAdapter:
    def optimise_spend(self, allocation: Dict[str, float], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimise spend on the ad platform (abstract)
        """
        raise NotImplementedError

    def fetch_performance(self, campaign_ids: list[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch campaign performance data (abstract)
        """
        raise NotImplementedError
