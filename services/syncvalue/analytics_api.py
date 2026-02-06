"""
Business Analytics API

Provides endpoints for the business performance dashboard
to track KIKI revenue, campaign performance, and ROI metrics.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from services.syncvalue.database import (
    get_db,
    init_db,
    CampaignRepository,
    PerformanceRepository,
    AnalyticsRepository
)
from shared.models import CampaignDeploymentModel, UserModel
from shared.auth_middleware import get_current_user, get_optional_user, verify_service_api_key

app = FastAPI(title="KIKI Analytics API", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()


# ============================================================================
# Response Models
# ============================================================================

class CampaignSummary(BaseModel):
    deployment_id: str
    brand_name: str
    campaign_type: str
    ltv_baseline: float
    budget: Optional[float]
    target_roi: Optional[float]
    deployment_status: str
    created_at: datetime
    deployed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PerformanceMetrics(BaseModel):
    date: datetime
    spend: float
    revenue: float
    conversions: int
    roi: Optional[float]
    cpa: Optional[float]


class BusinessSummary(BaseModel):
    total_campaigns: int
    active_campaigns: int
    spend_last_30_days: float
    revenue_last_30_days: float
    conversions_last_30_days: int
    kiki_revenue_last_30_days: float


class RevenueTrendPoint(BaseModel):
    date: datetime
    total_revenue: float
    total_spend: float
    kiki_performance_fee: float
    avg_roi: float


# ============================================================================
# Analytics Endpoints
# ============================================================================

@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/api/analytics/summary", response_model=BusinessSummary)
def get_business_summary(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get high-level business metrics (requires authentication)
    
    Returns:
        - Total campaigns created
        - Active campaigns
        - Last 30 days spend, revenue, conversions
        - KIKI revenue (20% performance fee)
    """
    analytics_repo = AnalyticsRepository(db)
    return analytics_repo.get_business_summary()


@app.get("/api/analytics/revenue-trend", response_model=List[RevenueTrendPoint])
def get_revenue_trend(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get daily revenue trend (requires authentication)
    
    Args:
        days: Number of days to retrieve (default 30)
    
    Returns:
        Daily revenue, spend, and KIKI fees
    """
    analytics_repo = AnalyticsRepository(db)
    summaries = analytics_repo.get_revenue_trend(days=days)
    
    return [
        RevenueTrendPoint(
            date=s.date,
            total_revenue=s.total_revenue,
            total_spend=s.total_spend,
            kiki_performance_fee=s.kiki_performance_fee,
            avg_roi=s.avg_roi
        )
        for s in summaries
    ]


@app.get("/api/campaigns", response_model=List[CampaignSummary])
def get_campaigns(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get list of campaigns (requires authentication)
    
    Args:
        limit: Max results to return
        offset: Pagination offset
        status: Filter by status (draft, deployed, active, etc.)
        user_id: Filter by user ID
    
    Returns:
        List of campaign summaries
    """
    campaign_repo = CampaignRepository(db)
    
    if user_id:
        campaigns = campaign_repo.get_campaigns_by_user(user_id, limit, offset)
    elif status and status.upper() == "ACTIVE":
        campaigns = campaign_repo.get_active_campaigns(limit)
    else:
        # Get all campaigns
        campaigns = db.query(CampaignDeploymentModel).order_by(
            CampaignDeploymentModel.created_at.desc()
        ).limit(limit).offset(offset).all()
    
    return [
        CampaignSummary(
            deployment_id=c.deployment_id,
            brand_name=c.brand_name,
            campaign_type=c.campaign_type.value,
            ltv_baseline=c.ltv_baseline,
            budget=c.budget,
            target_roi=c.target_roi,
            deployment_status=c.deployment_status.value,
            created_at=c.created_at,
            deployed_at=c.deployed_at
        )
        for c in campaigns
    ]


@app.get("/api/campaigns/{deployment_id}/performance", response_model=List[PerformanceMetrics])
def get_campaign_performance(
    deployment_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get performance metrics for a specific campaign (requires authentication)
    
    Args:
        deployment_id: Campaign deployment ID
        start_date: Filter from this date
        end_date: Filter to this date
    
    Returns:
        Daily performance metrics
    """
    campaign_repo = CampaignRepository(db)
    campaign = campaign_repo.get_campaign(deployment_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    perf_repo = PerformanceRepository(db)
    performance = perf_repo.get_campaign_performance(
        campaign.id,
        start_date,
        end_date
    )
    
    return [
        PerformanceMetrics(
            date=p.date,
            spend=p.spend,
            revenue=p.revenue,
            conversions=p.conversions,
            roi=p.actual_roi,
            cpa=p.cpa
        )
        for p in performance
    ]


@app.get("/api/analytics/platform-breakdown")
def get_platform_breakdown(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get performance breakdown by platform (Meta, Google, TikTok, etc.) - requires authentication
    
    Args:
        days: Number of days to analyze
    
    Returns:
        Spend and revenue by platform
    """
    from sqlalchemy import func
    from shared.models import PerformanceMetricModel
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        PerformanceMetricModel.platform,
        func.sum(PerformanceMetricModel.spend).label("total_spend"),
        func.sum(PerformanceMetricModel.revenue).label("total_revenue"),
        func.sum(PerformanceMetricModel.conversions).label("total_conversions")
    ).filter(
        PerformanceMetricModel.metric_date >= start_date
    ).group_by(
        PerformanceMetricModel.platform
    ).all()
    
    return [
        {
            "platform": r.platform or "unknown",
            "spend": float(r.total_spend or 0),
            "revenue": float(r.total_revenue or 0),
            "conversions": int(r.total_conversions or 0),
            "roi": float(r.total_revenue / r.total_spend) if r.total_spend > 0 else 0
        }
        for r in results
    ]


@app.get("/api/analytics/top-performers")
def get_top_performing_campaigns(
    limit: int = 10,
    metric: str = "roi",  # roi, revenue, conversions
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get top performing campaigns (requires authentication)
    
    Args:
        limit: Number of top campaigns
        metric: Sort by 'roi', 'revenue', or 'conversions'
        days: Time window in days
    
    Returns:
        Top performing campaigns ranked by metric
    """
    from sqlalchemy import func
    from shared.models import PerformanceMetricModel
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Build query based on metric
    if metric == "revenue":
        order_by = func.sum(PerformanceMetricModel.revenue).desc()
    elif metric == "conversions":
        order_by = func.sum(PerformanceMetricModel.conversions).desc()
    else:  # roi
        order_by = func.avg(PerformanceMetricModel.roi).desc()
    
    results = db.query(
        CampaignDeploymentModel.deployment_id,
        CampaignDeploymentModel.brand_name,
        CampaignDeploymentModel.campaign_type,
        func.sum(PerformanceMetricModel.spend).label("total_spend"),
        func.sum(PerformanceMetricModel.revenue).label("total_revenue"),
        func.sum(PerformanceMetricModel.conversions).label("total_conversions"),
        func.avg(PerformanceMetricModel.roi).label("avg_roi")
    ).join(
        PerformanceMetricModel,
        CampaignDeploymentModel.deployment_id == PerformanceMetricModel.deployment_id
    ).filter(
        PerformanceMetricModel.metric_date >= start_date
    ).group_by(
        CampaignDeploymentModel.deployment_id
    ).order_by(order_by).limit(limit).all()
    
    return [
        {
            "deployment_id": r.deployment_id,
            "brand_name": r.brand_name,
            "campaign_type": r.campaign_type.value,
            "spend": float(r.total_spend or 0),
            "revenue": float(r.total_revenue or 0),
            "conversions": int(r.total_conversions or 0),
            "roi": float(r.avg_roi or 0)
        }
        for r in results
    ]


# ============================================================================
# Data Ingestion (for SyncFlow to report performance)
# ============================================================================

class PerformanceUpdate(BaseModel):
    deployment_id: str
    date: datetime
    spend: float
    revenue: float
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    platform: Optional[str] = None


@app.post("/api/performance/report")
def report_performance(
    update: PerformanceUpdate,
    db: Session = Depends(get_db),
    service: str = Depends(verify_service_api_key)
):
    """
    Report campaign performance (called by SyncFlow with API key)
    
    Requires API key authentication (service-to-service)
    
    Args:
        update: Performance metrics for a campaign
    
    Returns:
        Success confirmation
    """
    campaign_repo = CampaignRepository(db)
    campaign = campaign_repo.get_campaign(update.deployment_id)
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    perf_repo = PerformanceRepository(db)
    perf_repo.log_performance(
        campaign_id=campaign.id,
        date=update.date,
        spend=update.spend,
        revenue=update.revenue,
        impressions=update.impressions,
        clicks=update.clicks,
        conversions=update.conversions,
        platform=update.platform
    )
    
    return {"status": "success", "deployment_id": update.deployment_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)
