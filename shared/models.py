"""
SQLAlchemy ORM Models for KIKI Agent Platform

Central database models for campaign deployments, assets, and analytics.
Used across all services for persistent storage.
"""

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


# ============================================================================
# Enums
# ============================================================================

class AssetSource(str, enum.Enum):
    """Asset source tracking"""
    GENERATED = "generated"
    USER_PROVIDED = "user_provided"
    HYBRID = "hybrid"


class DeploymentStatus(str, enum.Enum):
    """Campaign deployment status"""
    DRAFT = "draft"
    DEPLOYED = "deployed"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    SAFETY_HOLD = "safety_hold"


class CampaignType(str, enum.Enum):
    """Campaign types (matching Meta Advantage+)"""
    ASC = "ASC"  # Advantage+ Shopping Campaigns
    ALC = "ALC"  # Advantage+ Lead Campaigns
    AIC = "AIC"  # Advantage+ App Campaigns


class Platform(str, enum.Enum):
    """Advertising platforms"""
    META = "meta"
    GOOGLE = "google"
    TIKTOK = "tiktok"
    SNAPCHAT = "snapchat"
    PINTEREST = "pinterest"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


# ============================================================================
# Campaign Deployment Models
# ============================================================================

class CampaignDeploymentModel(Base):
    """
    Main campaign deployment table.
    
    Stores complete campaign state including AI-generated and user-provided assets.
    """
    __tablename__ = "campaign_deployments"
    
    # Primary key
    deployment_id = Column(String(50), primary_key=True, index=True)
    
    # Campaign metadata
    url = Column(String(500), nullable=True)  # Optional for prompt-based campaigns
    brand_name = Column(String(200), nullable=False, index=True)
    industry_category = Column(String(100), nullable=False, index=True)
    campaign_type = Column(SQLEnum(CampaignType), nullable=False)
    
    # Financial constraints
    budget = Column(Float, nullable=True)
    target_roi = Column(Float, nullable=True)
    ltv_baseline = Column(Float, nullable=False)
    max_cpa = Column(Float, nullable=True)
    
    # Asset source tracking
    assets_source = Column(SQLEnum(AssetSource), nullable=False, default=AssetSource.GENERATED)
    
    # Status and compliance
    brand_safe = Column(Boolean, default=False)
    compliance_status = Column(String(50), default="pending")
    deployment_status = Column(SQLEnum(DeploymentStatus), nullable=False, default=DeploymentStatus.DRAFT, index=True)
    
    # Deployment tracking
    syncflow_deployment_id = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    deployed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ad_copies = relationship("AdCopyModel", back_populates="deployment", cascade="all, delete-orphan")
    image_prompts = relationship("ImagePromptModel", back_populates="deployment", cascade="all, delete-orphan")
    video_prompts = relationship("VideoPromptModel", back_populates="deployment", cascade="all, delete-orphan")
    user_assets = relationship("UserAssetModel", back_populates="deployment", cascade="all, delete-orphan")
    platform_deployments = relationship("PlatformDeploymentModel", back_populates="deployment", cascade="all, delete-orphan")
    performance_metrics = relationship("PerformanceMetricModel", back_populates="deployment", cascade="all, delete-orphan")


class AdCopyModel(Base):
    """AI-generated ad copy variations"""
    __tablename__ = "ad_copies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    deployment_id = Column(String(50), ForeignKey("campaign_deployments.deployment_id"), nullable=False, index=True)
    copy_text = Column(Text, nullable=False)
    variation_number = Column(Integer, nullable=False)
    tone = Column(String(50), nullable=True)
    audience_segment = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    deployment = relationship("CampaignDeploymentModel", back_populates="ad_copies")


class ImagePromptModel(Base):
    """AI-generated Stable Diffusion image prompts"""
    __tablename__ = "image_prompts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    deployment_id = Column(String(50), ForeignKey("campaign_deployments.deployment_id"), nullable=False, index=True)
    prompt_text = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    aesthetic_score = Column(Float, nullable=True)
    variation_number = Column(Integer, nullable=False)
    
    # Generated image URL (after rendering)
    image_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    deployment = relationship("CampaignDeploymentModel", back_populates="image_prompts")


class VideoPromptModel(Base):
    """AI-generated video prompts for RunwayML/DeepBrain/D-ID"""
    __tablename__ = "video_prompts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    deployment_id = Column(String(50), ForeignKey("campaign_deployments.deployment_id"), nullable=False, index=True)
    prompt_text = Column(Text, nullable=False)
    camera_motion = Column(String(100), nullable=True)
    duration_seconds = Column(Integer, default=15)
    variation_number = Column(Integer, nullable=False)
    
    # Generated video URL (after rendering)
    video_url = Column(String(500), nullable=True)
    provider = Column(String(50), nullable=True)  # runwayml, deepbrain, did
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    deployment = relationship("CampaignDeploymentModel", back_populates="video_prompts")


class UserAssetModel(Base):
    """
    User-provided assets (BYOC - Bring Your Own Creative).
    
    Stores images, videos, ad copies, and descriptions provided by users.
    """
    __tablename__ = "user_assets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    deployment_id = Column(String(50), ForeignKey("campaign_deployments.deployment_id"), nullable=False, index=True)
    
    asset_type = Column(String(50), nullable=False)  # ad_copy, image, video, description
    asset_content = Column(Text, nullable=False)  # URL, text, or base64
    asset_metadata = Column(JSON, nullable=True)  # Additional metadata
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    deployment = relationship("CampaignDeploymentModel", back_populates="user_assets")


# ============================================================================
# Platform Deployment Tracking
# ============================================================================

class PlatformDeploymentModel(Base):
    """
    Track deployments across multiple advertising platforms.
    
    One campaign can be deployed to Meta, Google, TikTok simultaneously.
    """
    __tablename__ = "platform_deployments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    deployment_id = Column(String(50), ForeignKey("campaign_deployments.deployment_id"), nullable=False, index=True)
    
    platform = Column(SQLEnum(Platform), nullable=False, index=True)
    platform_campaign_id = Column(String(100), nullable=True)  # Platform's internal campaign ID
    platform_status = Column(String(50), default="pending")
    
    # Platform-specific config
    platform_config = Column(JSON, nullable=True)
    
    # Deployment tracking
    deployed_at = Column(DateTime, nullable=True)
    last_sync_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    deployment = relationship("CampaignDeploymentModel", back_populates="platform_deployments")


# ============================================================================
# Performance Analytics
# ============================================================================

class PerformanceMetricModel(Base):
    """
    Campaign performance metrics aggregated across platforms.
    
    Updated hourly via SyncFlow and platform APIs.
    """
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    deployment_id = Column(String(50), ForeignKey("campaign_deployments.deployment_id"), nullable=False, index=True)
    
    # Time range
    metric_date = Column(DateTime, nullable=False, index=True)
    
    # Spend and revenue
    spend = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    
    # Engagement metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    
    # Calculated metrics
    ctr = Column(Float, default=0.0)  # Click-through rate
    cpc = Column(Float, default=0.0)  # Cost per click
    cpa = Column(Float, default=0.0)  # Cost per acquisition
    roi = Column(Float, default=0.0)  # Return on investment
    
    # LTV metrics
    predicted_ltv = Column(Float, default=0.0)
    actual_ltv = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    deployment = relationship("CampaignDeploymentModel", back_populates="performance_metrics")


# ============================================================================
# User and Authentication
# ============================================================================

class UserModel(Base):
    """User accounts for KIKI Agent platform"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)  # Renamed from password_hash for consistency
    role = Column(String(50), default="user")  # user, admin, agency
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Profile
    full_name = Column(String(200), nullable=True)
    organization_id = Column(String(50), nullable=True, index=True)
    
    # Platform API keys (encrypted)
    meta_api_key = Column(Text, nullable=True)
    google_api_key = Column(Text, nullable=True)
    tiktok_api_key = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    campaigns = relationship("CampaignDeploymentModel", backref="user", foreign_keys="CampaignDeploymentModel.deployment_id")


# ============================================================================
# Invite Codes (for invite-only registration)
# ============================================================================

class InviteCodeModel(Base):
    """
    Invite codes for controlled user registration.
    
    Admin-generated one-time use tokens for B2B invite-only access.
    """
    __tablename__ = "invite_codes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), unique=True, nullable=False, index=True)  # Unique invite code
    
    # Tracking
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Admin who created it
    used_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # User who used it (null = unused)
    
    # Status
    is_used = Column(Boolean, default=False, nullable=False, index=True)
    is_revoked = Column(Boolean, default=False, nullable=False)  # Manual revocation
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True, index=True)  # Optional expiration
    
    # Relationships
    created_by = relationship("UserModel", foreign_keys=[created_by_id], backref="created_invites")
    used_by = relationship("UserModel", foreign_keys=[used_by_id], backref="used_invite")


# ============================================================================
# LTV Predictions Cache
# ============================================================================

class LTVPredictionModel(Base):
    """
    Cached LTV predictions from SyncValue dRNN model.
    
    Improves performance by avoiding repeated model inference.
    """
    __tablename__ = "ltv_predictions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    
    # Prediction inputs
    industry = Column(String(100), nullable=False)
    business_model = Column(String(50), nullable=True)
    
    # Prediction outputs
    predicted_ltv = Column(Float, nullable=False)
    confidence_score = Column(Float, default=0.0)
    
    # Model version
    model_version = Column(String(50), default="v1.0")
    
    # Timestamps
    predicted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Prediction TTL


# ============================================================================
# Audit Trail
# ============================================================================

class AuditLogModel(Base):
    """
    Comprehensive audit trail for compliance (SyncShield integration).
    
    Logs all campaign actions, deployments, and user operations.
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Event metadata
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSON, nullable=True)
    
    # User tracking
    user_id = Column(String(50), nullable=True, index=True)
    ip_address = Column(String(50), nullable=True)
    
    # Resource tracking
    deployment_id = Column(String(50), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ============================================================================
# Business Analytics (Daily Rollups)
# ============================================================================

class DailyRevenueSummaryModel(Base):
    """
    Daily revenue summary for business analytics dashboard.
    
    Materialized view updated daily via cron job for fast dashboard queries.
    """
    __tablename__ = "daily_revenue_summary"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    summary_date = Column(DateTime, nullable=False, unique=True, index=True)
    
    # Campaign counts
    total_campaigns = Column(Integer, default=0)
    active_campaigns = Column(Integer, default=0)
    deployed_campaigns = Column(Integer, default=0)
    
    # Financial metrics
    total_spend = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)
    total_conversions = Column(Integer, default=0)
    
    # Performance metrics
    avg_roi = Column(Float, default=0.0)
    avg_cpa = Column(Float, default=0.0)
    avg_ctr = Column(Float, default=0.0)
    
    # KIKI business metrics
    kiki_performance_fee = Column(Float, default=0.0)  # 20% of revenue
    kiki_clients_served = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# Database Initialization
# ============================================================================

def init_database(engine):
    """
    Initialize all database tables.
    
    Usage:
        from sqlalchemy import create_engine
        engine = create_engine('postgresql://...')
        init_database(engine)
    """
    Base.metadata.create_all(engine)


def drop_database(engine):
    """Drop all database tables (use with caution!)"""
    Base.metadata.drop_all(engine)
