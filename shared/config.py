"""
Shared configuration management for KIKI Agent services
Uses Pydantic BaseSettings for environment-based configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class ServiceConfig(BaseSettings):
    """Base configuration class with common settings"""
    
    # Service identity
    service_name: str = "kiki-service"
    environment: str = "development"
    version: str = "1.0.0"
    
    # API settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 1
    
    # Database settings
    database_url: str = "postgresql://kiki:kiki_pass@postgres:5432/kiki_db"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    
    # Redis settings
    redis_url: str = "redis://redis:6379/0"
    redis_max_connections: int = 50
    
    # Security settings
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # Internal API key for service-to-service communication
    internal_api_key: str = "internal-secret-key"
    
    # Monitoring settings
    enable_metrics: bool = True
    enable_tracing: bool = True
    log_level: str = "INFO"
    
    # External service URLs
    syncbrain_url: str = "http://syncbrain:8000"
    syncvalue_url: str = "http://syncvalue:8000"
    syncflow_url: str = "http://syncflow:8000"
    synccreate_url: str = "http://synccreate:8000"
    syncengage_url: str = "http://syncengage:8000"
    syncshield_url: str = "http://syncshield:8000"
    
    # Retry settings
    retry_max_attempts: int = 3
    retry_backoff_factor: float = 2.0
    retry_max_delay: int = 60
    
    # Graceful shutdown timeout
    shutdown_timeout: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"


class SyncBrainConfig(ServiceConfig):
    """SyncBrain-specific configuration"""
    service_name: str = "syncbrain"
    port: int = 8001
    
    # OpenAI settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.7
    context_window_size: int = 10


class SyncValueConfig(ServiceConfig):
    """SyncValue-specific configuration"""
    service_name: str = "syncvalue"
    port: int = 8002
    
    # Model settings
    ltv_model_path: str = "ltv_model.pt"
    model_input_size: int = 10
    model_hidden_size: int = 16
    batch_size: int = 32
    prediction_threshold: float = 0.5


class SyncCreateConfig(ServiceConfig):
    """SyncCreate-specific configuration"""
    service_name: str = "synccreate"
    port: int = 8004
    
    # Creative generation settings
    stability_api_key: Optional[str] = None
    runway_api_key: Optional[str] = None
    max_gen_time: int = 300
    
    # Brand safety settings
    brand_safety_threshold: float = 0.8


class SyncFlowConfig(ServiceConfig):
    """SyncFlow-specific configuration"""
    service_name: str = "syncflow"
    port: int = 8005
    
    # Bidding settings
    bid_timeout_ms: int = 100
    max_bid_amount: float = 10.0
    min_bid_amount: float = 0.01


class SyncEngageConfig(ServiceConfig):
    """SyncEngage-specific configuration"""
    service_name: str = "syncengage"
    port: int = 8007
    
    # CRM settings
    hubspot_api_key: Optional[str] = None
    salesforce_api_key: Optional[str] = None
    churn_threshold: float = 0.7


class SyncShieldConfig(ServiceConfig):
    """SyncShield-specific configuration"""
    service_name: str = "syncshield"
    port: int = 8006
    
    # Encryption settings
    encryption_key: str = "your-32-byte-encryption-key-here!!"
    enable_audit_logging: bool = True
    audit_log_retention_days: int = 90
