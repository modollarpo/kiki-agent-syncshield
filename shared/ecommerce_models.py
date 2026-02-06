"""
E-Commerce Integration Models for KIKI Agent™

Shared SQLAlchemy models for CMS platform integrations (Shopify, WooCommerce, Magento).
These models enable closed-loop revenue tracking and attribution.

Dependencies:
    - SQLAlchemy for ORM
    - PostgreSQL for production (SQLite for dev)
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Numeric, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from decimal import Decimal

Base = declarative_base()


# ========================================================================
# CMS Store Connections
# ========================================================================

class StoreConnectionModel(Base):
    """
    Represents a connected e-commerce store (Shopify, WooCommerce, Magento).
    Stores OAuth credentials and configuration.
    """
    __tablename__ = "store_connections"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Store identification
    platform = Column(String(50), nullable=False)  # "shopify", "woocommerce", "magento"
    store_name = Column(String(200), nullable=False)  # E.g., "my-store.myshopify.com"
    store_url = Column(String(500), nullable=False)
    
    # OAuth credentials (encrypted at rest by SyncShield™)
    access_token = Column(Text, nullable=False)  # OAuth access token
    refresh_token = Column(Text, nullable=True)  # For platforms that support refresh
    token_expires_at = Column(DateTime, nullable=True)
    
    # Platform-specific identifiers
    shop_id = Column(String(100), nullable=True)  # Shopify shop ID
    site_url = Column(String(500), nullable=True)  # WooCommerce site URL
    
    # Integration configuration
    webhook_secret = Column(String(200), nullable=True)  # For webhook verification
    sync_enabled = Column(Boolean, default=True, nullable=False)
    auto_sync_products = Column(Boolean, default=True, nullable=False)
    auto_sync_orders = Column(Boolean, default=True, nullable=False)
    
    # Historical baseline metadata
    baseline_start_date = Column(DateTime, nullable=True)  # Start of 12-month baseline
    baseline_end_date = Column(DateTime, nullable=True)    # End of baseline period
    baseline_revenue = Column(Numeric(12, 2), nullable=True)  # Pre-KIKI revenue
    baseline_order_count = Column(Integer, default=0)
    baseline_avg_order_value = Column(Numeric(10, 2), nullable=True)
    
    # Sync status
    last_product_sync = Column(DateTime, nullable=True)
    last_order_sync = Column(DateTime, nullable=True)
    last_inventory_sync = Column(DateTime, nullable=True)
    
    # Timestamps
    connected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = relationship("ProductModel", back_populates="store", cascade="all, delete-orphan")
    orders = relationship("OrderModel", back_populates="store", cascade="all, delete-orphan")
    customers = relationship("CustomerModel", back_populates="store", cascade="all, delete-orphan")


# ========================================================================
# Product Catalog
# ========================================================================

class ProductModel(Base):
    """
    Synced product from CMS. Used for creative generation and inventory tracking.
    """
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("store_connections.id"), nullable=False, index=True)
    
    # Platform identifiers
    platform_product_id = Column(String(100), nullable=False, index=True)  # Shop-specific ID
    sku = Column(String(100), nullable=True, index=True)
    
    # Product details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    product_type = Column(String(200), nullable=True)  # Category/type
    vendor = Column(String(200), nullable=True)
    
    # Pricing
    price = Column(Numeric(10, 2), nullable=False)
    compare_at_price = Column(Numeric(10, 2), nullable=True)  # Original price (for discounts)
    cost_per_item = Column(Numeric(10, 2), nullable=True)  # COGS (for margin calc)
    
    # Inventory
    inventory_quantity = Column(Integer, default=0, nullable=False)
    inventory_tracked = Column(Boolean, default=True, nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False, index=True)
    low_stock_threshold = Column(Integer, default=10, nullable=False)
    
    # Media assets (for SyncCreate™)
    image_url = Column(String(1000), nullable=True)
    images = Column(JSON, nullable=True)  # List of all image URLs
    video_url = Column(String(1000), nullable=True)
    
    # Product URLs
    product_url = Column(String(1000), nullable=True)
    admin_url = Column(String(1000), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_published = Column(Boolean, default=True, nullable=False)
    
    # KIKI-specific metadata
    auto_pause_ads = Column(Boolean, default=True, nullable=False)  # Pause ads when out of stock
    ltv_category_weight = Column(Float, default=1.0)  # Category weight for LTV prediction
    
    # Performance metrics (calculated by SyncValue™)
    total_revenue = Column(Numeric(12, 2), default=0)
    total_orders = Column(Integer, default=0)
    avg_customer_ltv = Column(Numeric(10, 2), nullable=True)
    conversion_rate = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    synced_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    store = relationship("StoreConnectionModel", back_populates="products")
    order_items = relationship("OrderItemModel", back_populates="product")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_product_store_platform_id', 'store_id', 'platform_product_id', unique=True),
        Index('idx_product_active_stock', 'is_active', 'in_stock'),
    )


# ========================================================================
# Customer Data
# ========================================================================

class CustomerModel(Base):
    """
    Synced customer from CMS. Used for LTV prediction and segmentation.
    """
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("store_connections.id"), nullable=False, index=True)
    
    # Platform identifiers
    platform_customer_id = Column(String(100), nullable=False, index=True)
    
    # Customer details (PII - encrypted by SyncShield™)
    email = Column(String(255), nullable=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Segmentation
    total_orders = Column(Integer, default=0, nullable=False)
    total_spent = Column(Numeric(12, 2), default=0, nullable=False)
    avg_order_value = Column(Numeric(10, 2), nullable=True)
    
    # LTV metrics (calculated by SyncValue™)
    predicted_ltv = Column(Numeric(10, 2), nullable=True)
    ltv_confidence = Column(Float, nullable=True)  # 0.0 - 1.0
    churn_risk_score = Column(Float, nullable=True)  # 0.0 (low) - 1.0 (high)
    
    # Purchase behavior
    first_order_date = Column(DateTime, nullable=True)
    last_order_date = Column(DateTime, nullable=True)
    days_since_last_order = Column(Integer, nullable=True)
    purchase_frequency = Column(Float, nullable=True)  # Orders per month
    
    # Acquisition attribution (set by SyncFlow™)
    acquired_via_kiki = Column(Boolean, default=False, nullable=False)
    acquisition_campaign_id = Column(String(100), nullable=True)
    acquisition_cost = Column(Numeric(10, 2), nullable=True)
    
    # Engagement status (for SyncEngage™)
    opted_in_email = Column(Boolean, default=False, nullable=False)
    opted_in_sms = Column(Boolean, default=False, nullable=False)
    last_engagement_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    synced_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    store = relationship("StoreConnectionModel", back_populates="customers")
    orders = relationship("OrderModel", back_populates="customer")
    
    # Indexes
    __table_args__ = (
        Index('idx_customer_store_platform_id', 'store_id', 'platform_customer_id', unique=True),
        Index('idx_customer_ltv', 'predicted_ltv'),
        Index('idx_customer_churn', 'churn_risk_score'),
    )


# ========================================================================
# Order Tracking
# ========================================================================

class OrderModel(Base):
    """
    Synced order from CMS. Used for attribution and OaaS settlement.
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("store_connections.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    
    # Platform identifiers
    platform_order_id = Column(String(100), nullable=False, index=True)
    order_number = Column(String(100), nullable=False)
    
    # Order details
    total_price = Column(Numeric(10, 2), nullable=False)
    subtotal_price = Column(Numeric(10, 2), nullable=False)
    total_tax = Column(Numeric(10, 2), default=0)
    total_shipping = Column(Numeric(10, 2), default=0)
    total_discounts = Column(Numeric(10, 2), default=0)
    
    # Financial tracking
    currency = Column(String(10), default="USD", nullable=False)
    financial_status = Column(String(50), nullable=True)  # "paid", "pending", "refunded"
    fulfillment_status = Column(String(50), nullable=True)  # "fulfilled", "unfulfilled"
    
    # Attribution (set by SyncLedger™)
    attributed_to_kiki = Column(Boolean, default=False, nullable=False, index=True)
    attribution_confidence = Column(Float, nullable=True)  # 0.0 - 1.0
    campaign_id = Column(String(100), nullable=True, index=True)
    touchpoint_ids = Column(JSON, nullable=True)  # List of ad interactions
    
    # Revenue classification
    is_baseline = Column(Boolean, default=False, nullable=False)  # Pre-KIKI order
    is_incremental = Column(Boolean, default=False, nullable=False)  # Uplift order
    incremental_revenue = Column(Numeric(10, 2), default=0)
    
    # Customer lifecycle
    is_first_order = Column(Boolean, default=False, nullable=False)
    is_repeat_order = Column(Boolean, default=False, nullable=False)
    customer_order_number = Column(Integer, nullable=True)  # 1st, 2nd, 3rd order
    
    # Timestamps
    order_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    synced_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    store = relationship("StoreConnectionModel", back_populates="orders")
    customer = relationship("CustomerModel", back_populates="orders")
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_order_store_platform_id', 'store_id', 'platform_order_id', unique=True),
        Index('idx_order_attribution', 'attributed_to_kiki', 'is_incremental'),
        Index('idx_order_date', 'order_date'),
    )


class OrderItemModel(Base):
    """
    Individual line items within an order.
    """
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    
    # Platform identifiers
    platform_line_item_id = Column(String(100), nullable=False)
    platform_product_id = Column(String(100), nullable=True)
    sku = Column(String(100), nullable=True)
    
    # Item details
    product_title = Column(String(500), nullable=False)
    variant_title = Column(String(500), nullable=True)
    quantity = Column(Integer, nullable=False)
    
    # Pricing
    price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    order = relationship("OrderModel", back_populates="items")
    product = relationship("ProductModel", back_populates="order_items")


# ========================================================================
# Inventory Events (for Circuit Breaker)
# ========================================================================

class InventoryEventModel(Base):
    """
    Tracks inventory changes for real-time circuit breaker triggers.
    """
    __tablename__ = "inventory_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False)  # "restock", "out_of_stock", "low_stock"
    previous_quantity = Column(Integer, nullable=False)
    new_quantity = Column(Integer, nullable=False)
    quantity_change = Column(Integer, nullable=False)
    
    # Circuit breaker actions
    triggered_ad_pause = Column(Boolean, default=False, nullable=False)
    triggered_ad_resume = Column(Boolean, default=False, nullable=False)
    affected_campaign_ids = Column(JSON, nullable=True)  # List of paused campaigns
    
    # Timestamps
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_inventory_event_product_date', 'product_id', 'occurred_at'),
    )


# ========================================================================
# Webhook Log (for debugging)
# ========================================================================

class WebhookLogModel(Base):
    """
    Logs all incoming webhooks from CMS platforms for debugging and replay.
    """
    __tablename__ = "webhook_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("store_connections.id"), nullable=False, index=True)
    
    # Webhook details
    platform = Column(String(50), nullable=False)
    topic = Column(String(200), nullable=False, index=True)  # E.g., "orders/create"
    webhook_id = Column(String(200), nullable=True)
    
    # Request details
    payload = Column(JSON, nullable=False)  # Full webhook payload
    headers = Column(JSON, nullable=True)
    signature = Column(String(500), nullable=True)
    verified = Column(Boolean, default=False, nullable=False)
    
    # Processing status
    processed = Column(Boolean, default=False, nullable=False, index=True)
    processing_error = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_webhook_store_topic', 'store_id', 'topic'),
        Index('idx_webhook_processed', 'processed', 'received_at'),
    )
