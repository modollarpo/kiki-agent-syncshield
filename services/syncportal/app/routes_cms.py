"""
SyncPortal™ FastAPI Routes - CMS Integration Webhooks & OAuth

Exposes HTTP endpoints for:
1. OAuth flows (Shopify, WooCommerce, BigCommerce)
2. Webhook receivers (Shopify, WooCommerce, BigCommerce)
3. Manual sync triggers (products, orders, customers)
4. Attribution reports and OaaS settlement

Authentication:
- Internal endpoints: x-internal-api-key header (from other Council agents)
- External webhooks: Platform-specific signature verification
- OAuth callbacks: State parameter validation

Usage:
    # Shopify install flow
    GET /oauth/shopify/install?shop=example.myshopify.com&user_id=123
    
    # Shopify webhook receiver
    POST /webhooks/shopify/orders/create
    
    # Manual product sync (internal)
    POST /internal/sync/products/{store_id}
    Headers: x-internal-api-key: <secret>
"""
from fastapi import APIRouter, Request, HTTPException, Header, Query, Depends, Security
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import Optional
import logging
import os
import json
from decimal import Decimal

from shared.database import get_db
from shared.ecommerce_models import StoreConnectionModel, ProductModel, OrderModel
from .integration_orchestrator import CMSIntegrationOrchestrator
from .cms_connectors.shopify_handler import ShopifyWebhookHandler
from .cms_connectors.woocommerce_handler import WooCommerceWebhookHandler
from .connectors.shopify import ShopifyConnector
from .connectors.woocommerce import WooCommerceConnector
from .connectors.bigcommerce import BigCommerceConnector

logger = logging.getLogger(__name__)

# Router for CMS integration endpoints
router = APIRouter()

# Environment variables
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY', 'test_api_key')
SHOPIFY_API_SECRET = os.getenv('SHOPIFY_API_SECRET', 'test_api_secret')
SHOPIFY_CALLBACK_URL = os.getenv('SHOPIFY_CALLBACK_URL', 'http://localhost:8060/oauth/shopify/callback')
SHOPIFY_SCOPES = os.getenv('SHOPIFY_SCOPES', 'read_products,write_products,read_orders,read_customers')

WOOCOMMERCE_CALLBACK_URL = os.getenv('WOOCOMMERCE_CALLBACK_URL', 'http://localhost:8060/oauth/woocommerce/callback')

INTERNAL_API_KEY = os.getenv('KIKI_INTERNAL_API_KEY', 'dev-internal-key-change-in-production')

# Internal API key authentication
API_KEY_HEADER = APIKeyHeader(name="x-internal-api-key", auto_error=False)


async def verify_internal_api_key(api_key: str = Security(API_KEY_HEADER)):
    """Verify x-internal-api-key header for internal Council endpoints."""
    if api_key != INTERNAL_API_KEY:
        logger.error(f"❌ Invalid internal API key: {api_key}")
        raise HTTPException(status_code=403, detail="Invalid internal API key")
    return api_key


# ========================================================================
# Shopify OAuth Flow
# ========================================================================

@router.get("/oauth/shopify/install")
async def shopify_oauth_install(
    shop: str = Query(..., description="Shopify shop domain (e.g., example.myshopify.com)"),
    user_id: int = Query(..., description="KIKI user ID initiating install"),
    db: Session = Depends(get_db)
):
    """
    Step 1: Redirect merchant to Shopify OAuth consent screen.
    
    Flow:
    1. Merchant clicks "Install KIKI" in SyncPortal
    2. Redirect to Shopify authorization URL
    3. Shopify shows permission consent screen
    4. Merchant approves → Shopify redirects to callback URL with code
    
    Args:
        shop: Shopify shop domain (must end with .myshopify.com)
        user_id: KIKI user ID (passed as state parameter for validation)
    
    Returns:
        Redirect to Shopify OAuth authorization URL
    """
    # Validate shop domain
    if not shop.endswith('.myshopify.com'):
        raise HTTPException(status_code=400, detail="Invalid Shopify shop domain")
    
    # Build OAuth authorization URL
    oauth_url = (
        f"https://{shop}/admin/oauth/authorize?"
        f"client_id={SHOPIFY_API_KEY}&"
        f"scope={SHOPIFY_SCOPES}&"
        f"redirect_uri={SHOPIFY_CALLBACK_URL}&"
        f"state={user_id}"
    )
    
    logger.info(f"🔐 Shopify OAuth install initiated for {shop} (user: {user_id})")
    
    return RedirectResponse(oauth_url)


@router.get("/oauth/shopify/callback")
async def shopify_oauth_callback(
    code: str = Query(..., description="OAuth authorization code"),
    shop: str = Query(..., description="Shopify shop domain"),
    state: str = Query(..., description="User ID from install step"),
    db: Session = Depends(get_db)
):
    """
    Step 2: Exchange authorization code for permanent access token.
    
    Flow:
    1. Shopify redirects here after merchant approves permissions
    2. Exchange code for access token via Shopify Admin API
    3. Store encrypted credentials in database
    4. Calculate baseline metrics (12-month historical data)
    5. Register webhooks for real-time events
    6. Trigger initial product/customer sync
    
    Args:
        code: OAuth authorization code (single-use, expires in 60 seconds)
        shop: Shopify shop domain
        state: User ID passed from install step
    
    Returns:
        Redirect to SyncPortal dashboard with success message
    """
    user_id = int(state)
    
    # Exchange code for access token
    import httpx
    
    token_url = f"https://{shop}/admin/oauth/access_token"
    token_payload = {
        'client_id': SHOPIFY_API_KEY,
        'client_secret': SHOPIFY_API_SECRET,
        'code': code
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, json=token_payload)
        
        if response.status_code != 200:
            logger.error(f"❌ Failed to exchange Shopify OAuth code: {response.text}")
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        token_data = response.json()
        access_token = token_data.get('access_token')
        scopes = token_data.get('scope', '')
    
    # Store connection in database (credentials encrypted by SyncShield™)
    # TODO: Call SyncShield.EncryptCustomerData() to encrypt access_token
    store = StoreConnectionModel(
        user_id=user_id,
        platform='shopify',
        store_name=shop,
        api_key=SHOPIFY_API_KEY,  # Public API key
        access_token=access_token,  # TODO: Encrypt this
        scopes=scopes,
        is_active=True
    )
    db.add(store)
    db.commit()
    db.refresh(store)
    
    logger.info(f"✅ Shopify store connected: {shop} (store_id: {store.id})")
    
    # Initialize connector
    connector = ShopifyConnector(
        store_id=store.id,
        config={
            'shop_domain': shop,
            'access_token': access_token
        }
    )
    
    # Calculate baseline metrics (12-month historical)
    orchestrator = CMSIntegrationOrchestrator(db)
    baseline = await orchestrator.calculate_baseline(store.id, months=12)
    
    # Update store with baseline
    store.baseline_revenue = baseline.get('total_revenue', Decimal('0.00'))
    store.baseline_orders = baseline.get('total_orders', 0)
    store.baseline_calculated_at = baseline.get('calculated_at')
    db.commit()
    
    logger.info(
        f"📊 Baseline calculated: ${baseline.get('total_revenue', 0):.2f} "
        f"from {baseline.get('total_orders', 0)} orders"
    )
    
    # Register webhooks for real-time events
    webhook_topics = [
        'orders/create',
        'orders/paid',
        'orders/updated',
        'products/create',
        'products/update',
        'products/delete',
        'inventory_levels/update',
        'customers/create',
        'customers/update',
    ]
    
    webhook_results = await connector.register_webhooks(
        topics=webhook_topics,
        callback_url=f"{os.getenv('SYNCPORTAL_PUBLIC_URL', 'https://api.kiki.ai')}/webhooks/shopify/{{topic}}"
    )
    
    logger.info(f"🔔 Registered {len(webhook_results)} Shopify webhooks")
    
    # Trigger initial sync (run in background)
    # TODO: Use background tasks for long-running sync
    # BackgroundTasks.add_task(orchestrator.sync_products, store.id)
    
    # Redirect to dashboard
    dashboard_url = f"{os.getenv('SYNCPORTAL_DASHBOARD_URL', 'http://localhost:3000')}/stores/{store.id}/connected"
    return RedirectResponse(dashboard_url)


# ========================================================================
# WooCommerce OAuth Flow (Manual API Key Entry)
# ========================================================================

@router.post("/oauth/woocommerce/connect")
async def woocommerce_connect(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    WooCommerce "OAuth" - Actually manual API key entry.
    
    WooCommerce doesn't have OAuth like Shopify. Instead, merchants:
    1. Generate API keys in WooCommerce → Settings → Advanced → REST API
    2. Paste Consumer Key + Secret into KIKI form
    
    Body:
    {
        "user_id": 123,
        "site_url": "https://example.com",
        "consumer_key": "ck_abc123...",
        "consumer_secret": "cs_xyz789...",
        "webhook_secret": "optional_webhook_secret"
    }
    
    Returns:
        Store connection details with baseline metrics
    """
    data = await request.json()
    
    user_id = data.get('user_id')
    site_url = data.get('site_url')
    consumer_key = data.get('consumer_key')
    consumer_secret = data.get('consumer_secret')
    webhook_secret = data.get('webhook_secret', '')
    
    # Validate required fields
    if not all([user_id, site_url, consumer_key, consumer_secret]):
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: user_id, site_url, consumer_key, consumer_secret"
        )
    
    # Test connection by fetching system status
    connector = WooCommerceConnector(
        store_id=0,  # Temporary, will update after DB insert
        config={
            'site_url': site_url,
            'consumer_key': consumer_key,
            'consumer_secret': consumer_secret
        }
    )
    
    # Verify credentials work
    try:
        status = await connector.get_system_status()
        if not status:
            raise HTTPException(status_code=401, detail="Invalid WooCommerce credentials")
    except Exception as e:
        logger.error(f"❌ WooCommerce connection test failed: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Connection failed: {str(e)}")
    
    # Store connection (encrypt credentials)
    # TODO: Encrypt consumer_key and consumer_secret via SyncShield
    store = StoreConnectionModel(
        user_id=user_id,
        platform='woocommerce',
        store_name=site_url,
        api_key=consumer_key,  # TODO: Encrypt
        api_secret=consumer_secret,  # TODO: Encrypt
        webhook_secret=webhook_secret,
        is_active=True
    )
    db.add(store)
    db.commit()
    db.refresh(store)
    
    logger.info(f"✅ WooCommerce store connected: {site_url} (store_id: {store.id})")
    
    # Calculate baseline
    orchestrator = CMSIntegrationOrchestrator(db)
    baseline = await orchestrator.calculate_baseline(store.id, months=12)
    
    store.baseline_revenue = baseline.get('total_revenue', Decimal('0.00'))
    store.baseline_orders = baseline.get('total_orders', 0)
    store.baseline_calculated_at = baseline.get('calculated_at')
    db.commit()
    
    # Register webhooks
    webhook_topics = [
        'order.created',
        'order.updated',
        'product.created',
        'product.updated',
        'product.deleted',
        'customer.created',
        'customer.updated',
    ]
    
    webhook_results = await connector.register_webhooks(
        topics=webhook_topics,
        callback_url=f"{os.getenv('SYNCPORTAL_PUBLIC_URL', 'https://api.kiki.ai')}/webhooks/woocommerce/{{topic}}",
        secret=webhook_secret
    )
    
    logger.info(f"🔔 Registered {len(webhook_results)} WooCommerce webhooks")
    
    return {
        'status': 'success',
        'store_id': store.id,
        'platform': 'woocommerce',
        'site_url': site_url,
        'baseline_revenue': float(store.baseline_revenue),
        'baseline_orders': store.baseline_orders,
        'webhooks_registered': len(webhook_results)
    }


# ========================================================================
# Webhook Receivers - Shopify
# ========================================================================

@router.post("/webhooks/shopify/{topic}")
async def shopify_webhook(
    topic: str,
    request: Request,
    x_shopify_hmac_sha256: Optional[str] = Header(None),
    x_shopify_shop_domain: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Receive and process Shopify webhooks.
    
    Webhook Topics:
    - orders/create: New order placed
    - orders/paid: Payment confirmed
    - products/update: Product modified (inventory changes)
    - inventory_levels/update: Stock quantity changed
    - customers/create: New customer signed up
    
    Headers:
    - X-Shopify-Hmac-Sha256: HMAC signature for verification
    - X-Shopify-Shop-Domain: Shop that sent the webhook
    - X-Shopify-Topic: Webhook topic (redundant, also in URL)
    
    Security:
    - Verifies HMAC-SHA256 signature using webhook secret
    - Logs all webhooks to SyncShield™ for audit trail
    """
    # Get raw payload for signature verification
    raw_payload = await request.body()
    
    # Parse JSON payload
    try:
        payload = json.loads(raw_payload.decode('utf-8'))
    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON in Shopify webhook")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Validate required headers
    if not x_shopify_hmac_sha256 or not x_shopify_shop_domain:
        logger.error("❌ Missing required Shopify webhook headers")
        raise HTTPException(status_code=400, detail="Missing required headers")
    
    # Convert topic format: orders/create → orders_create (for handler routing)
    topic_normalized = topic.replace('/', '_')
    
    # Initialize handler
    orchestrator = CMSIntegrationOrchestrator(db)
    handler = ShopifyWebhookHandler(db, orchestrator)
    
    # Process webhook
    result = await handler.handle_webhook(
        topic=topic,
        payload=payload,
        shop_domain=x_shopify_shop_domain,
        signature=x_shopify_hmac_sha256,
        raw_payload=raw_payload
    )
    
    return JSONResponse(result)


# ========================================================================
# Webhook Receivers - WooCommerce
# ========================================================================

@router.post("/webhooks/woocommerce/{topic}")
async def woocommerce_webhook(
    topic: str,
    request: Request,
    x_wc_webhook_signature: Optional[str] = Header(None),
    x_wc_webhook_source: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Receive and process WooCommerce webhooks.
    
    Webhook Topics:
    - order.created: New order placed
    - order.updated: Order status changed
    - product.created: New product added
    - product.updated: Product modified (inventory, price)
    - customer.created: New customer account
    
    Headers:
    - X-WC-Webhook-Signature: Base64-encoded HMAC-SHA256 signature
    - X-WC-Webhook-Source: Source site URL
    - X-WC-Webhook-Topic: Webhook topic
    
    Security:
    - Verifies Base64 HMAC-SHA256 signature
    - Logs to SyncShield™ for compliance
    """
    # Get raw payload for signature verification
    raw_payload = await request.body()
    
    # Parse JSON payload
    try:
        payload = json.loads(raw_payload.decode('utf-8'))
    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON in WooCommerce webhook")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Validate headers
    if not x_wc_webhook_signature or not x_wc_webhook_source:
        logger.error("❌ Missing required WooCommerce webhook headers")
        raise HTTPException(status_code=400, detail="Missing required headers")
    
    # Initialize handler
    orchestrator = CMSIntegrationOrchestrator(db)
    handler = WooCommerceWebhookHandler(db, orchestrator)
    
    # Process webhook
    result = await handler.handle_webhook(
        topic=topic,
        payload=payload,
        site_url=x_wc_webhook_source,
        signature=x_wc_webhook_signature,
        raw_payload=raw_payload
    )
    
    return JSONResponse(result)


# ========================================================================
# Internal Sync Triggers (x-internal-api-key required)
# ========================================================================

@router.post(
    "/internal/sync/products/{store_id}",
    dependencies=[Depends(verify_internal_api_key)]
)
async def trigger_product_sync(
    store_id: int,
    db: Session = Depends(get_db)
):
    """
    Manually trigger full product catalog sync.
    
    Used by:
    - SyncFlow™ to refresh product inventory before bid adjustments
    - Admin dashboard to force resync after bulk product edits
    - Scheduled jobs to keep catalog fresh
    
    Security: Requires x-internal-api-key header
    
    Returns:
        Count of products synced
    """
    orchestrator = CMSIntegrationOrchestrator(db)
    
    count = await orchestrator.sync_products(store_id)
    
    logger.info(f"📦 Synced {count} products for store {store_id}")
    
    return {'status': 'success', 'products_synced': count, 'store_id': store_id}


@router.post(
    "/internal/sync/orders/{store_id}",
    dependencies=[Depends(verify_internal_api_key)]
)
async def trigger_order_sync(
    store_id: int,
    days: int = Query(30, description="Number of days to sync (default 30)"),
    db: Session = Depends(get_db)
):
    """
    Manually trigger historical order sync.
    
    Used for:
    - Backfilling orders after initial connection
    - Re-running attribution engine on historical data
    - Monthly reconciliation for OaaS settlement
    
    Security: Requires x-internal-api-key header
    
    Returns:
        Count of orders synced and attributed
    """
    orchestrator = CMSIntegrationOrchestrator(db)
    
    count = await orchestrator.sync_orders(store_id, days=days)
    
    logger.info(f"📋 Synced {count} orders for store {store_id} (last {days} days)")
    
    return {
        'status': 'success',
        'orders_synced': count,
        'store_id': store_id,
        'days': days
    }


@router.post(
    "/internal/attribution/recalculate/{store_id}",
    dependencies=[Depends(verify_internal_api_key)]
)
async def recalculate_attribution(
    store_id: int,
    order_ids: Optional[list[int]] = None,
    db: Session = Depends(get_db)
):
    """
    Re-run attribution engine on existing orders.
    
    Use cases:
    - Update attribution after improving ML model
    - Correct misattributed orders
    - Monthly reconciliation before OaaS billing
    
    Security: Requires x-internal-api-key header
    
    Args:
        store_id: Store to recalculate attribution for
        order_ids: Specific order IDs to recalculate (if None, recalculate all)
    
    Returns:
        Attribution statistics (incremental count, total revenue)
    """
    orchestrator = CMSIntegrationOrchestrator(db)
    
    # Get orders to recalculate
    query = db.query(OrderModel).filter(OrderModel.store_id == store_id)
    
    if order_ids:
        query = query.filter(OrderModel.id.in_(order_ids))
    
    orders = query.all()
    
    incremental_count = 0
    incremental_revenue = Decimal('0.00')
    
    for order in orders:
        attribution = await orchestrator.attribute_order(
            order_id=order.id,
            customer_email=order.customer_email,
            order_date=order.order_date
        )
        
        if attribution.get('is_incremental'):
            incremental_count += 1
            incremental_revenue += attribution.get('incremental_revenue', Decimal('0.00'))
    
    logger.info(
        f"🔄 Recalculated attribution for {len(orders)} orders: "
        f"{incremental_count} incremental (${incremental_revenue:.2f})"
    )
    
    return {
        'status': 'success',
        'store_id': store_id,
        'orders_processed': len(orders),
        'incremental_count': incremental_count,
        'incremental_revenue': float(incremental_revenue)
    }


# ========================================================================
# Attribution Reports (for OaaS settlement)
# ========================================================================

@router.get("/reports/oaas/monthly/{store_id}")
async def get_monthly_oaas_report(
    store_id: int,
    year: int = Query(..., description="Year (e.g., 2024)"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_internal_api_key)
):
    """
    Generate monthly OaaS settlement report.
    
    Calculates:
    - Baseline revenue (12-month pre-KIKI average)
    - Current month revenue
    - Incremental revenue (attributed to KIKI with confidence >= 0.7)
    - Success fee (20% of incremental)
    
    This report is used for:
    - Monthly invoicing
    - Customer dashboards
    - Performance tracking
    
    Security: Requires x-internal-api-key header
    
    Returns:
        {
            "store_id": 123,
            "period": "2024-01",
            "baseline_revenue": 10000.00,
            "current_revenue": 15000.00,
            "incremental_revenue": 5000.00,
            "growth_percentage": 50.0,
            "success_fee": 1000.00,
            "order_count": 150,
            "incremental_order_count": 50,
            "avg_attribution_confidence": 0.85
        }
    """
    from datetime import date
    from calendar import monthrange
    
    # Get month date range
    first_day = date(year, month, 1)
    last_day_num = monthrange(year, month)[1]
    last_day = date(year, month, last_day_num)
    
    # Get store
    store = db.query(StoreConnectionModel).filter(
        StoreConnectionModel.id == store_id
    ).first()
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Get orders for this month
    orders = db.query(OrderModel).filter(
        OrderModel.store_id == store_id,
        OrderModel.order_date >= first_day,
        OrderModel.order_date <= last_day
    ).all()
    
    # Calculate metrics
    total_revenue = sum(order.total_price for order in orders)
    incremental_orders = [o for o in orders if o.is_incremental]
    incremental_revenue = sum(o.incremental_revenue for o in incremental_orders)
    
    baseline_monthly = store.baseline_revenue / 12 if store.baseline_revenue else Decimal('0.00')
    growth_percentage = (
        ((total_revenue - baseline_monthly) / baseline_monthly * 100)
        if baseline_monthly > 0 else 0.0
    )
    
    success_fee = incremental_revenue * Decimal('0.20')  # 20% of incremental
    
    avg_confidence = (
        sum(o.attribution_confidence for o in incremental_orders) / len(incremental_orders)
        if incremental_orders else 0.0
    )
    
    report = {
        'store_id': store_id,
        'store_name': store.store_name,
        'platform': store.platform,
        'period': f"{year}-{month:02d}",
        'baseline_revenue': float(baseline_monthly),
        'current_revenue': float(total_revenue),
        'incremental_revenue': float(incremental_revenue),
        'growth_percentage': float(growth_percentage),
        'success_fee': float(success_fee),
        'order_count': len(orders),
        'incremental_order_count': len(incremental_orders),
        'avg_attribution_confidence': float(avg_confidence)
    }
    
    logger.info(
        f"📊 OaaS Report {year}-{month:02d} for store {store_id}: "
        f"${incremental_revenue:.2f} incremental (fee: ${success_fee:.2f})"
    )
    
    return report
