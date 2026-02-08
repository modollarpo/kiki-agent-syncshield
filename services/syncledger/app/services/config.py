"""
Configuration for Ad Spend Fetcher Service

Loads credentials from environment variables for all 6 supported platforms.
All tokens are stored in HashiCorp Vault in production.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class AdPlatformSettings(BaseSettings):
    """Settings for multi-platform ad spend fetching"""
    
    # ========================================================================
    # META ADS (Facebook/Instagram) - Already configured
    # ========================================================================
    meta_app_id: Optional[str] = os.getenv("META_APP_ID")
    meta_app_secret: Optional[str] = os.getenv("META_APP_SECRET")
    meta_access_token: Optional[str] = os.getenv("META_ACCESS_TOKEN")
    
    # ========================================================================
    # GOOGLE ADS - Already configured
    # ========================================================================
    google_ads_credentials_path: Optional[str] = os.getenv(
        "GOOGLE_ADS_CREDENTIALS_PATH",
        "/etc/kiki/google-ads.yaml"
    )
    
    # ========================================================================
    # TIKTOK ADS - NEW (Phase 1)
    # ========================================================================
    tiktok_app_id: Optional[str] = os.getenv("TIKTOK_APP_ID")
    tiktok_app_secret: Optional[str] = os.getenv("TIKTOK_APP_SECRET")
    tiktok_access_token: Optional[str] = os.getenv("TIKTOK_ACCESS_TOKEN")
    
    # ========================================================================
    # LINKEDIN ADS - NEW (Phase 1)
    # ========================================================================
    linkedin_client_id: Optional[str] = os.getenv("LINKEDIN_CLIENT_ID")
    linkedin_client_secret: Optional[str] = os.getenv("LINKEDIN_CLIENT_SECRET")
    linkedin_access_token: Optional[str] = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    # ========================================================================
    # AMAZON ADVERTISING - NEW (Phase 2)
    # ========================================================================
    amazon_client_id: Optional[str] = os.getenv("AMAZON_CLIENT_ID")
    amazon_client_secret: Optional[str] = os.getenv("AMAZON_CLIENT_SECRET")
    amazon_access_token: Optional[str] = os.getenv("AMAZON_ACCESS_TOKEN")
    amazon_refresh_token: Optional[str] = os.getenv("AMAZON_REFRESH_TOKEN")
    
    # ========================================================================
    # MICROSOFT ADVERTISING (Bing) - NEW (Phase 2)
    # ========================================================================
    microsoft_client_id: Optional[str] = os.getenv("MICROSOFT_CLIENT_ID")
    microsoft_client_secret: Optional[str] = os.getenv("MICROSOFT_CLIENT_SECRET")
    microsoft_developer_token: Optional[str] = os.getenv("MICROSOFT_DEVELOPER_TOKEN")
    microsoft_customer_id: Optional[str] = os.getenv("MICROSOFT_CUSTOMER_ID")
    microsoft_access_token: Optional[str] = os.getenv("MICROSOFT_ACCESS_TOKEN")
    
    # ========================================================================
    # FUTURE PLATFORMS (Phase 3)
    # ========================================================================
    snapchat_org_id: Optional[str] = os.getenv("SNAPCHAT_ORG_ID")
    snapchat_access_token: Optional[str] = os.getenv("SNAPCHAT_ACCESS_TOKEN")
    
    pinterest_ad_account_id: Optional[str] = os.getenv("PINTEREST_AD_ACCOUNT_ID")
    pinterest_access_token: Optional[str] = os.getenv("PINTEREST_ACCESS_TOKEN")
    
    reddit_account_id: Optional[str] = os.getenv("REDDIT_ACCOUNT_ID")
    reddit_access_token: Optional[str] = os.getenv("REDDIT_ACCESS_TOKEN")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = AdPlatformSettings()
