"""
Interface for consuming SyncValue™ predictions
- Abstracts external ML system
- All calls are mocked/stubbed for tests
"""
from typing import List, Dict

def get_ltv_predictions(campaigns: List[str]) -> Dict[str, float]:
    """
    Fetch predicted LTV for each campaign from SyncValue™ (stubbed)
    """
    # In production, this would call SyncValue via gRPC/REST
    # Here, we return mocked predictions
    return {c: 100.0 + i * 10.0 for i, c in enumerate(campaigns)}
