"""
SyncValue - GetPlatformLTV gRPC Endpoint
Provides average LTV metrics per advertising platform for GlobalBudgetOptimizer
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from enum import Enum
import random

router = APIRouter(prefix="/platform-ltv", tags=["Platform LTV"])


class Platform(str, Enum):
    META = "PLATFORM_META"
    GOOGLE = "PLATFORM_GOOGLE"
    TIKTOK = "PLATFORM_TIKTOK"
    LINKEDIN = "PLATFORM_LINKEDIN"
    AMAZON = "PLATFORM_AMAZON"
    MICROSOFT = "PLATFORM_MICROSOFT"


class PlatformLTVRequest(BaseModel):
    client_id: str
    platform: Platform
    lookback_days: int = 90


class PlatformLTVResponse(BaseModel):
    platform: Platform
    average_ltv: float
    p25_ltv: float  # 25th percentile
    p75_ltv: float  # 75th percentile
    sample_size: int


# Placeholder LTV database (will be replaced with actual ML model predictions)
PLATFORM_LTV_DATA: Dict[Platform, Dict[str, float]] = {
    Platform.META: {"average": 450.0, "p25": 320.0, "p75": 580.0},
    Platform.GOOGLE: {"average": 480.0, "p25": 350.0, "p75": 610.0},
    Platform.TIKTOK: {"average": 420.0, "p25": 300.0, "p75": 540.0},
    Platform.LINKEDIN: {"average": 440.0, "p25": 330.0, "p75": 550.0},
    Platform.AMAZON: {"average": 460.0, "p25": 340.0, "p75": 590.0},
    Platform.MICROSOFT: {"average": 470.0, "p25": 360.0, "p75": 600.0},
}


@router.post("", response_model=PlatformLTVResponse)
async def get_platform_ltv(request: PlatformLTVRequest) -> PlatformLTVResponse:
    """
    Get average LTV for users acquired via a specific advertising platform.
    
    This endpoint is called by GlobalBudgetOptimizer to calculate LTV-to-CAC ratios
    and determine optimal budget allocation across platforms.
    
    Args:
        request: Client ID, platform, and lookback period
        
    Returns:
        PlatformLTVResponse with average LTV, percentiles, and sample size
        
    Example:
        POST /platform-ltv
        {
            "client_id": "demo-client-001",
            "platform": "PLATFORM_META",
            "lookback_days": 90
        }
        
        Response:
        {
            "platform": "PLATFORM_META",
            "average_ltv": 450.0,
            "p25_ltv": 320.0,
            "p75_ltv": 580.0,
            "sample_size": 1247
        }
    """
    # Validate platform
    if request.platform not in PLATFORM_LTV_DATA:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown platform: {request.platform}"
        )
    
    # Get LTV data for platform
    ltv_data = PLATFORM_LTV_DATA[request.platform]
    
    # TODO: Replace with actual ML model prediction from PostgreSQL
    # This would query the ltv_predictions table filtered by:
    # - client_id
    # - acquisition_platform = platform
    # - prediction_date >= (today - lookback_days)
    # Then calculate avg, p25, p75 using NumPy/Pandas
    
    return PlatformLTVResponse(
        platform=request.platform,
        average_ltv=ltv_data["average"],
        p25_ltv=ltv_data["p25"],
        p75_ltv=ltv_data["p75"],
        sample_size=random.randint(1000, 1500)  # Placeholder
    )


@router.get("/{platform}", response_model=PlatformLTVResponse)
async def get_platform_ltv_by_path(
    platform: Platform,
    client_id: str = "demo-client-001",
    lookback_days: int = 90
) -> PlatformLTVResponse:
    """
    Alternative GET endpoint for platform LTV (convenience method).
    
    Example:
        GET /platform-ltv/PLATFORM_META?client_id=demo-client-001&lookback_days=90
    """
    request = PlatformLTVRequest(
        client_id=client_id,
        platform=platform,
        lookback_days=lookback_days
    )
    return await get_platform_ltv(request)
