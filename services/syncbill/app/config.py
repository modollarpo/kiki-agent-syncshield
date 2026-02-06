"""
Configuration for SyncBill™

Environment Variables:
- DATABASE_URL: PostgreSQL connection string
- STRIPE_SECRET_KEY: Stripe API secret key
- STRIPE_WEBHOOK_SECRET: Stripe webhook signing secret
- SYNCLEDGER_HOST: SyncLedger gRPC host
- SYNCLEDGER_PORT: SyncLedger gRPC port
- KIKI_INTERNAL_API_KEY: Internal service authentication
- HTTP_PORT: FastAPI server port (default 8095)
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Service configuration
    service_name: str = "syncbill"
    http_port: int = int(os.getenv("HTTP_PORT", "8095"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://kiki:password@localhost:5432/kiki_billing"
    )
    
    # Stripe configuration
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    stripe_publishable_key: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    
    # SyncLedger gRPC connection
    syncledger_host: str = os.getenv("SYNCLEDGER_HOST", "localhost")
    syncledger_port: int = int(os.getenv("SYNCLEDGER_PORT", "50053"))
    
    # Internal authentication
    internal_api_key: str = os.getenv(
        "KIKI_INTERNAL_API_KEY",
        "dev-internal-key-change-in-production"
    )
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",  # SyncPortal frontend
        "http://localhost:8080",  # API Gateway
    ]
    
    # Invoice configuration
    company_name: str = "KIKI Agent™"
    company_email: str = "billing@kikiagent.ai"
    company_address: str = "1 Innovation Drive, San Francisco, CA 94102"
    invoice_due_days: int = 30  # Net 30 payment terms
    
    # Tax configuration
    default_tax_rate: float = 0.0  # No tax by default
    eu_vat_rate: float = 0.20  # 20% VAT for EU customers
    uk_vat_rate: float = 0.20  # 20% VAT for UK customers
    
    # Credit memo configuration
    auto_issue_credits: bool = True  # Automatically issue credits for rollbacks
    
    # PDF generation
    pdf_storage_path: str = os.getenv("PDF_STORAGE_PATH", "/tmp/invoices")
    pdf_base_url: str = os.getenv("PDF_BASE_URL", "https://billing.kikiagent.ai/invoices")
    
    # Notification
    send_invoice_emails: bool = True
    invoice_email_template: str = "invoice_notification.html"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
