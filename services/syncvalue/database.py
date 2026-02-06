"""
Database Layer for Campaign Persistence

Provides repository pattern for storing and retrieving campaign data.
Enterprise-grade with connection pooling, migrations, and monitoring.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import os
import logging

# Import from shared models (single source of truth)
from shared.models import (
    Base,
    CampaignDeploymentModel,
    AdCopyModel,
    ImagePromptModel,
    VideoPromptModel,
    UserAssetModel,
    PlatformDeploymentModel,
    PerformanceMetricModel,
    DailyRevenueSummaryModel,
    DeploymentStatus,
    AssetSource,
    CampaignType,
    Platform
)

logger = logging.getLogger(__name__)

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kiki_campaigns.db")

# Connection pool settings (enterprise-grade)
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "40"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 hour

# Create engine with enterprise configuration
if "sqlite" in DATABASE_URL:
    # SQLite-specific settings (development only)
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true"
    )
else:
    # PostgreSQL/MySQL production settings
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        poolclass=QueuePool,
        pool_size=POOL_SIZE,
        max_overflow=MAX_OVERFLOW,
        pool_timeout=POOL_TIMEOUT,
        pool_recycle=POOL_RECYCLE,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
        execution_options={
            "isolation_level": "READ COMMITTED"
        }
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize database tables.
    
    For production, use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")


def get_db() -> Session:
    """
    Get database session (FastAPI dependency).
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Get database session as context manager.
    
    Usage:
        with get_db_context() as db:
            result = db.query(Model).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ============================================================================
# Campaign Repository
# ============================================================================

class CampaignRepository:
    """Repository for campaign CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_campaign(
        self,
        deployment_id: str,
        brand_name: str,
        industry_category: str,
        campaign_type: str,
        ltv_baseline: float,
        url: Optional[str] = None,
        prompt: Optional[str] = None,
        budget: Optional[float] = None,
        target_roi: Optional[float] = None,
        max_cpa: Optional[float] = None,
        assets_source: str = "generated",
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> CampaignDeployment:
        """Create new campaign deployment"""
        
        campaign = CampaignDeployment(
            deployment_id=deployment_id,
            url=url,
            prompt=prompt,
            brand_name=brand_name,
            industry_category=industry_category,
            campaign_type=CampaignType[campaign_type],
            ltv_baseline=ltv_baseline,
            budget=budget,
            target_roi=target_roi,
            max_cpa=max_cpa,
            assets_source=AssetSource[assets_source.upper()],
            user_id=user_id,
            organization_id=organization_id
        )
        
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        
        return campaign
    
    def add_ad_copies(self, campaign_id: int, ad_copies: List[str]):
        """Add AI-generated ad copies"""
        for copy in ad_copies:
            ad_copy = AdCopy(campaign_id=campaign_id, content=copy)
            self.db.add(ad_copy)
        self.db.commit()
    
    def add_image_prompts(self, campaign_id: int, prompts: List[str]):
        """Add AI-generated image prompts"""
        for prompt in prompts:
            img_prompt = ImagePrompt(campaign_id=campaign_id, prompt=prompt)
            self.db.add(img_prompt)
        self.db.commit()
    
    def add_video_prompts(self, campaign_id: int, prompts: List[str]):
        """Add AI-generated video prompts"""
        for prompt in prompts:
            vid_prompt = VideoPrompt(campaign_id=campaign_id, prompt=prompt)
            self.db.add(vid_prompt)
        self.db.commit()
    
    def add_user_assets(
        self,
        campaign_id: int,
        asset_type: str,
        content: Optional[str] = None,
        url: Optional[str] = None
    ):
        """Add user-provided assets (BYOC)"""
        asset = UserAsset(
            campaign_id=campaign_id,
            asset_type=asset_type,
            content=content,
            url=url
        )
        self.db.add(asset)
        self.db.commit()
    
    def get_campaign(self, deployment_id: str) -> Optional[CampaignDeployment]:
        """Get campaign by deployment ID"""
        return self.db.query(CampaignDeployment).filter(
            CampaignDeployment.deployment_id == deployment_id
        ).first()
    
    def get_campaigns_by_user(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[CampaignDeployment]:
        """Get campaigns for a specific user"""
        return self.db.query(CampaignDeployment).filter(
            CampaignDeployment.user_id == user_id
        ).order_by(CampaignDeployment.created_at.desc()).limit(limit).offset(offset).all()
    
    def get_active_campaigns(self, limit: int = 100) -> List[CampaignDeployment]:
        """Get all active campaigns"""
        return self.db.query(CampaignDeployment).filter(
            CampaignDeployment.deployment_status == DeploymentStatus.ACTIVE
        ).limit(limit).all()
    
    def update_deployment_status(
        self,
        deployment_id: str,
        status: str,
        syncflow_deployment_id: Optional[str] = None
    ):
        """Update campaign deployment status"""
        campaign = self.get_campaign(deployment_id)
        if campaign:
            campaign.deployment_status = DeploymentStatus[status.upper()]
            if syncflow_deployment_id:
                campaign.syncflow_deployment_id = syncflow_deployment_id
            if status.lower() == "deployed":
                campaign.deployed_at = datetime.utcnow()
            self.db.commit()


# ============================================================================
# Performance Repository
# ============================================================================

class PerformanceRepository:
    """Repository for campaign performance metrics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_performance(
        self,
        campaign_id: int,
        date: datetime,
        spend: float,
        revenue: float,
        impressions: int = 0,
        clicks: int = 0,
        conversions: int = 0,
        platform: Optional[str] = None
    ) -> CampaignPerformance:
        """Log daily performance metrics"""
        
        # Calculate derived metrics
        ctr = (clicks / impressions * 100) if impressions > 0 else None
        cpc = (spend / clicks) if clicks > 0 else None
        cpa = (spend / conversions) if conversions > 0 else None
        roas = (revenue / spend) if spend > 0 else None
        actual_roi = (revenue / spend) if spend > 0 else None
        
        performance = CampaignPerformance(
            campaign_id=campaign_id,
            date=date,
            spend=spend,
            revenue=revenue,
            impressions=impressions,
            clicks=clicks,
            conversions=conversions,
            ctr=ctr,
            cpc=cpc,
            cpa=cpa,
            roas=roas,
            actual_roi=actual_roi,
            platform=platform
        )
        
        self.db.add(performance)
        self.db.commit()
        self.db.refresh(performance)
        
        return performance
    
    def get_campaign_performance(
        self,
        campaign_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CampaignPerformance]:
        """Get performance metrics for a campaign"""
        query = self.db.query(CampaignPerformance).filter(
            CampaignPerformance.campaign_id == campaign_id
        )
        
        if start_date:
            query = query.filter(CampaignPerformance.date >= start_date)
        if end_date:
            query = query.filter(CampaignPerformance.date <= end_date)
        
        return query.order_by(CampaignPerformance.date.asc()).all()
    
    def get_total_performance(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get aggregated performance across all campaigns"""
        query = self.db.query(
            func.sum(CampaignPerformance.spend).label("total_spend"),
            func.sum(CampaignPerformance.revenue).label("total_revenue"),
            func.sum(CampaignPerformance.conversions).label("total_conversions"),
            func.avg(CampaignPerformance.actual_roi).label("avg_roi"),
            func.avg(CampaignPerformance.cpa).label("avg_cpa")
        )
        
        if start_date:
            query = query.filter(CampaignPerformance.date >= start_date)
        if end_date:
            query = query.filter(CampaignPerformance.date <= end_date)
        
        result = query.first()
        
        return {
            "total_spend": float(result.total_spend or 0),
            "total_revenue": float(result.total_revenue or 0),
            "total_conversions": int(result.total_conversions or 0),
            "avg_roi": float(result.avg_roi or 0),
            "avg_cpa": float(result.avg_cpa or 0)
        }


# ============================================================================
# Analytics Repository
# ============================================================================

class AnalyticsRepository:
    """Repository for business analytics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def update_daily_summary(self, date: datetime):
        """Update daily revenue summary (run daily via cron)"""
        
        # Get all performance for the date
        perf_data = self.db.query(
            func.count(func.distinct(CampaignPerformance.campaign_id)).label("total_campaigns"),
            func.sum(CampaignPerformance.spend).label("total_spend"),
            func.sum(CampaignPerformance.revenue).label("total_revenue"),
            func.sum(CampaignPerformance.conversions).label("total_conversions"),
            func.avg(CampaignPerformance.actual_roi).label("avg_roi"),
            func.avg(CampaignPerformance.cpa).label("avg_cpa")
        ).filter(
            CampaignPerformance.date == date
        ).first()
        
        # Count active campaigns
        active_campaigns = self.db.query(CampaignDeployment).filter(
            CampaignDeployment.deployment_status == DeploymentStatus.ACTIVE
        ).count()
        
        # Calculate KIKI performance fee (20% of revenue)
        total_revenue = float(perf_data.total_revenue or 0)
        kiki_fee = total_revenue * 0.20
        
        # Upsert daily summary
        summary = self.db.query(DailyRevenueSummary).filter(
            DailyRevenueSummary.date == date
        ).first()
        
        if summary:
            # Update existing
            summary.total_campaigns = perf_data.total_campaigns or 0
            summary.active_campaigns = active_campaigns
            summary.total_spend = float(perf_data.total_spend or 0)
            summary.total_revenue = total_revenue
            summary.total_conversions = int(perf_data.total_conversions or 0)
            summary.avg_roi = float(perf_data.avg_roi or 0)
            summary.avg_cpa = float(perf_data.avg_cpa or 0)
            summary.kiki_performance_fee = kiki_fee
            summary.updated_at = datetime.utcnow()
        else:
            # Insert new
            summary = DailyRevenueSummary(
                date=date,
                total_campaigns=perf_data.total_campaigns or 0,
                active_campaigns=active_campaigns,
                total_spend=float(perf_data.total_spend or 0),
                total_revenue=total_revenue,
                total_conversions=int(perf_data.total_conversions or 0),
                avg_roi=float(perf_data.avg_roi or 0),
                avg_cpa=float(perf_data.avg_cpa or 0),
                kiki_performance_fee=kiki_fee
            )
            self.db.add(summary)
        
        self.db.commit()
        return summary
    
    def get_revenue_trend(self, days: int = 30) -> List[DailyRevenueSummary]:
        """Get revenue trend for last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return self.db.query(DailyRevenueSummary).filter(
            DailyRevenueSummary.date >= start_date
        ).order_by(DailyRevenueSummary.date.asc()).all()
    
    def get_business_summary(self) -> Dict[str, Any]:
        """Get high-level business metrics"""
        
        # Last 30 days performance
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        perf = self.db.query(
            func.sum(CampaignPerformance.spend).label("spend_30d"),
            func.sum(CampaignPerformance.revenue).label("revenue_30d"),
            func.sum(CampaignPerformance.conversions).label("conversions_30d")
        ).filter(
            CampaignPerformance.date >= thirty_days_ago
        ).first()
        
        # Campaign counts
        total_campaigns = self.db.query(CampaignDeployment).count()
        active_campaigns = self.db.query(CampaignDeployment).filter(
            CampaignDeployment.deployment_status == DeploymentStatus.ACTIVE
        ).count()
        
        # Calculate KIKI revenue
        revenue_30d = float(perf.revenue_30d or 0)
        kiki_revenue_30d = revenue_30d * 0.20
        
        return {
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "spend_last_30_days": float(perf.spend_30d or 0),
            "revenue_last_30_days": revenue_30d,
            "conversions_last_30_days": int(perf.conversions_30d or 0),
            "kiki_revenue_last_30_days": kiki_revenue_30d
        }
