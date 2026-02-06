"""
WooCommerce Webhook Handler for SyncPortal™

Processes real-time webhooks from WooCommerce CMS platform and coordinates
actions across the Council of Nine agents.

Webhook Topics Handled:
- order.created → Attribution + SyncLedger + SyncEngage
- order.updated → Refund/cancellation handling
- product.created → Generate ad creatives
- product.updated → Circuit breaker + inventory sync
- customer.created → Initialize LTV tracking
- customer.updated → Update profile and LTV

Architecture Flow:
    WooCommerce → Webhook → Verify Signature → Log to SyncShield™ →
    Process Event → Notify Council Agents → Store in DB

Key Differences from Shopify:
- Signature: Base64-encoded HMAC-SHA256 (vs raw hex in Shopify)
- Payload structure: Different field names (e.g., billing.email vs customer.email)
- Stock status: "instock"/"outofstock" string (vs integer quantity)
"""
import hmac
import hashlib
import base64
import json
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException
import logging

from .council_clients import CouncilOfNineClients
from .integration_orchestrator import CMSIntegrationOrchestrator
from shared.ecommerce_models import (
    StoreConnectionModel,
    ProductModel,
    OrderModel,
    CustomerModel,
    WebhookLogModel,
)

logger = logging.getLogger(__name__)


class WooCommerceWebhookHandler:
    """
    Handles all WooCommerce webhook events with Council of Nine integration.
    """
    
    def __init__(self, db, orchestrator: CMSIntegrationOrchestrator):
        self.db = db
        self.orchestrator = orchestrator
        self.council = CouncilOfNineClients()
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str
    ) -> bool:
        """
        Verify WooCommerce webhook signature (Base64-encoded HMAC-SHA256).
        
        Args:
            payload: Raw webhook payload bytes
            signature: X-WC-Webhook-Signature header value (base64 encoded)
            secret: Webhook secret from store connection
        
        Returns:
            True if signature is valid
        """
        computed_hmac = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).digest()
        
        # WooCommerce uses base64 encoding (different from Shopify's hex)
        computed_signature = base64.b64encode(computed_hmac).decode('utf-8')
        
        return hmac.compare_digest(computed_signature, signature)
    
    async def handle_webhook(
        self,
        topic: str,
        payload: Dict[str, Any],
        site_url: str,
        signature: str,
        raw_payload: bytes
    ) -> Dict[str, Any]:
        """
        Main webhook processing dispatcher.
        
        Args:
            topic: Webhook topic (e.g., "order.created")
            payload: Parsed JSON payload
            site_url: WooCommerce site URL
            signature: Base64 HMAC signature for verification
            raw_payload: Raw bytes for signature verification
        
        Returns:
            Processing result dictionary
        """
        # Find store connection by site URL
        store = self.db.query(StoreConnectionModel).filter(
            StoreConnectionModel.store_name == site_url,
            StoreConnectionModel.platform == 'woocommerce'
        ).first()
        
        if not store:
            logger.error(f"❌ Store not found: {site_url}")
            return {'status': 'error', 'message': 'Store not found'}
        
        # Verify webhook signature
        verified = self.verify_webhook_signature(
            raw_payload,
            signature,
            store.webhook_secret or ''
        )
        
        if not verified:
            logger.error(f"❌ Invalid webhook signature from {site_url}")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Log webhook to SyncShield™ for audit trail
        await self.council.syncshield.log_webhook_event(
            platform="woocommerce",
            topic=topic,
            payload_json=json.dumps(payload),
            signature=signature,
            verified=verified,
            store_id=store.id
        )
        
        # Route to appropriate handler
        handlers = {
            'order.created': self.handle_order_created,
            'order.updated': self.handle_order_updated,
            'product.created': self.handle_product_created,
            'product.updated': self.handle_product_updated,
            'product.deleted': self.handle_product_deleted,
            'customer.created': self.handle_customer_created,
            'customer.updated': self.handle_customer_updated,
        }
        
        handler = handlers.get(topic)
        if not handler:
            logger.warning(f"⚠️  No handler for topic: {topic}")
            return {'status': 'skipped', 'message': f'No handler for {topic}'}
        
        # Process webhook
        try:
            result = await handler(store, payload)
            logger.info(f"✅ Processed WooCommerce webhook: {topic} for {site_url}")
            return result
        except Exception as e:
            logger.error(f"❌ Error processing webhook {topic}: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    # ========================================================================
    # Order Webhooks
    # ========================================================================
    
    async def handle_order_created(
        self,
        store: StoreConnectionModel,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process order.created webhook.
        
        Actions:
        1. Create order in database
        2. Run attribution engine
        3. Notify SyncLedger™ if incremental
        4. Update customer LTV in SyncValue™
        5. Trigger SyncEngage™ post-purchase flow
        
        WooCommerce Payload Structure:
        {
            "id": 123,
            "status": "processing",
            "total": "129.99",
            "billing": {"email": "customer@example.com", "first_name": "John", ...},
            "line_items": [{"product_id": 456, "quantity": 2, "total": "99.99"}, ...],
            "date_created": "2024-01-15T10:30:00"
        }
        """
        order_id = str(payload.get('id'))
        billing = payload.get('billing', {})
        customer_email = billing.get('email', '')
        total_price = Decimal(str(payload.get('total', '0.00')))
        
        # Use orchestrator to create order and run attribution
        result = await self.orchestrator.process_webhook(
            store_id=store.id,
            topic='order.created',
            payload=payload
        )
        
        if not result.get('status') == 'success':
            return result
        
        # Get attribution result
        attribution = result.get('attribution', {})
        is_incremental = attribution.get('is_incremental', False)
        confidence = attribution.get('confidence', 0.0)
        
        # Update customer LTV in SyncValue™
        if customer_email:
            # Check if this is first order (query customer table)
            customer = self.db.query(CustomerModel).filter(
                CustomerModel.store_id == store.id,
                CustomerModel.email == customer_email
            ).first()
            
            is_first_order = customer is None or customer.total_orders == 1
            
            ltv_result = await self.council.syncvalue.update_customer_ltv(
                store_id=store.id,
                customer_email=customer_email,
                order_amount=total_price,
                is_first_order=is_first_order,
                order_date=datetime.fromisoformat(
                    payload.get('date_created', datetime.utcnow().isoformat())
                ),
                customer_data={
                    'first_name': billing.get('first_name', ''),
                    'last_name': billing.get('last_name', ''),
                    'phone': billing.get('phone', ''),
                }
            )
            
            logger.info(
                f"📊 SyncValue updated LTV: ${ltv_result.get('predicted_ltv', 0):.2f} "
                f"(confidence: {ltv_result.get('confidence', 0):.2f})"
            )
        
        # Record incremental revenue in SyncLedger™
        if is_incremental:
            incremental_amount = attribution.get('incremental_revenue', total_price)
            
            ledger_result = await self.council.syncledger.record_incremental_revenue(
                store_id=store.id,
                order_id=result.get('order_db_id', 0),
                platform_order_id=order_id,
                order_amount=total_price,
                incremental_amount=incremental_amount,
                attribution_confidence=confidence,
                campaign_id=attribution.get('campaign_id'),
                touchpoint_ids=attribution.get('touchpoint_ids', [])
            )
            
            logger.info(
                f"💰 SyncLedger recorded ${incremental_amount:.2f} incremental "
                f"(success fee: ${ledger_result.get('success_fee_amount', 0):.2f})"
            )
        
        # Trigger SyncEngage™ post-purchase flow
        # WooCommerce doesn't have explicit marketing consent in order webhook
        # Check if customer exists and has marketing consent
        if customer_email and customer and getattr(customer, 'accepts_marketing', True):
            engage_result = await self.council.syncengage.trigger_post_purchase_flow(
                store_id=store.id,
                customer_data={
                    'email': customer_email,
                    'first_name': billing.get('first_name', ''),
                    'last_name': billing.get('last_name', ''),
                },
                order_id=result.get('order_db_id', 0),
                order_amount=total_price,
                items=payload.get('line_items', [])
            )
            
            logger.info(
                f"💌 SyncEngage triggered flow: {engage_result.get('flow_id', 'N/A')} "
                f"({len(engage_result.get('scheduled_emails', []))} emails scheduled)"
            )
        
        return {
            'status': 'success',
            'order_id': order_id,
            'attributed_to_kiki': is_incremental,
            'attribution_confidence': confidence,
            'ltv_updated': True,
            'engagement_triggered': bool(customer_email and customer)
        }
    
    async def handle_order_updated(
        self,
        store: StoreConnectionModel,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process order.updated webhook (order status changed).
        
        WooCommerce order statuses:
        - pending: Payment not received
        - processing: Payment received, processing order
        - on-hold: Awaiting payment
        - completed: Order fulfilled
        - cancelled: Cancelled by admin
        - refunded: Refunded by admin
        - failed: Payment failed
        
        Important for OaaS: Deduct refunded/cancelled amounts.
        """
        order_id = str(payload.get('id'))
        status = payload.get('status')
        total = Decimal(str(payload.get('total', '0.00')))
        
        # Update order in database
        order = self.db.query(OrderModel).filter(
            OrderModel.store_id == store.id,
            OrderModel.platform_order_id == order_id
        ).first()
        
        if order:
            # Map WooCommerce status to our model
            financial_status_map = {
                'pending': 'pending',
                'processing': 'processing',
                'completed': 'paid',
                'on-hold': 'pending',
                'cancelled': 'voided',
                'refunded': 'refunded',
                'failed': 'voided'
            }
            
            order.financial_status = financial_status_map.get(status, status)
            
            # If refunded/cancelled, adjust incremental revenue
            if status in ['refunded', 'cancelled'] and order.is_incremental:
                # Full refund/cancellation
                logger.warning(
                    f"⚠️  Order {order_id} {status}: "
                    f"${order.incremental_revenue:.2f} removed from OaaS"
                )
                
                order.incremental_revenue = Decimal('0.00')
                order.is_incremental = False
                
                # TODO: Notify SyncLedger™ to adjust monthly totals
                # await self.council.syncledger.adjust_incremental_revenue(...)
            
            self.db.commit()
        
        return {
            'status': 'success',
            'order_id': order_id,
            'order_status': status,
            'financial_status': order.financial_status if order else None
        }
    
    # ========================================================================
    # Product Webhooks
    # ========================================================================
    
    async def handle_product_created(
        self,
        store: StoreConnectionModel,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process product.created webhook (new product added).
        
        Actions:
        1. Sync product to database
        2. Trigger SyncCreate™ to generate ad creatives
        
        WooCommerce Payload:
        {
            "id": 789,
            "name": "Premium Widget",
            "price": "49.99",
            "regular_price": "59.99",
            "stock_quantity": 100,
            "stock_status": "instock",
            "images": [{"src": "https://..."}, ...]
        }
        """
        product_id = str(payload.get('id'))
        title = payload.get('name', '')
        price = Decimal(str(payload.get('price', '0.00')))
        stock_quantity = payload.get('stock_quantity', 0)
        stock_status = payload.get('stock_status', 'instock')
        
        # Create product in database
        product = ProductModel(
            store_id=store.id,
            platform_product_id=product_id,
            title=title,
            price=price,
            inventory_quantity=stock_quantity or 0,
            in_stock=(stock_status == 'instock'),
            product_url=payload.get('permalink', ''),
            image_url=payload.get('images', [{}])[0].get('src', '') if payload.get('images') else '',
            synced_at=datetime.utcnow()
        )
        self.db.add(product)
        self.db.commit()
        
        # Trigger SyncCreate™ to generate ad creatives
        creative_result = await self.council.synccreate.generate_product_creative(
            store_id=store.id,
            product_data={
                'id': product_id,
                'title': title,
                'price': float(price),
                'images': [img.get('src') for img in payload.get('images', [])],
                'description': payload.get('description', ''),
                'short_description': payload.get('short_description', ''),
            },
            creative_type="image",
            ad_network="meta"
        )
        
        logger.info(
            f"🎨 SyncCreate generated creative for {title} "
            f"(ID: {creative_result.get('creative_id', 'N/A')})"
        )
        
        return {
            'status': 'success',
            'product_id': product_id,
            'creative_generated': creative_result.get('success', False),
            'creative_id': creative_result.get('creative_id')
        }
    
    async def handle_product_updated(
        self,
        store: StoreConnectionModel,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process product.updated webhook (product modified).
        
        Actions:
        1. Update product in database
        2. Check inventory changes for circuit breaker
        3. Refresh ad creatives if images changed
        
        WooCommerce uses stock_status: "instock"/"outofstock" instead of integer quantity.
        """
        product_id = str(payload.get('id'))
        
        # Find product in database
        product = self.db.query(ProductModel).filter(
            ProductModel.store_id == store.id,
            ProductModel.platform_product_id == product_id
        ).first()
        
        if product:
            old_inventory = product.inventory_quantity
            old_in_stock = product.in_stock
            
            # Update product fields from webhook
            new_stock_quantity = payload.get('stock_quantity', 0) or 0
            new_stock_status = payload.get('stock_status', 'instock')
            new_in_stock = (new_stock_status == 'instock')
            
            product.title = payload.get('name', product.title)
            product.price = Decimal(str(payload.get('price', product.price)))
            product.inventory_quantity = new_stock_quantity
            product.in_stock = new_in_stock
            product.synced_at = datetime.utcnow()
            
            self.db.commit()
            
            # Check circuit breaker if stock status changed
            # WooCommerce: "instock" → "outofstock" triggers pause
            if old_in_stock and not new_in_stock:
                circuit_result = await self.orchestrator.check_inventory_circuit_breaker(
                    product.id,
                    0  # Treat out-of-stock as quantity = 0
                )
                
                return {
                    'status': 'success',
                    'product_id': product_id,
                    'stock_status_changed': True,
                    'circuit_breaker_action': circuit_result.get('action'),
                    'affected_campaigns': circuit_result.get('affected_campaigns', [])
                }
            
            # Resume campaigns if restocked
            elif not old_in_stock and new_in_stock:
                circuit_result = await self.orchestrator.check_inventory_circuit_breaker(
                    product.id,
                    new_stock_quantity or 999  # Non-zero to trigger resume
                )
                
                return {
                    'status': 'success',
                    'product_id': product_id,
                    'stock_status_changed': True,
                    'circuit_breaker_action': circuit_result.get('action'),
                    'affected_campaigns': circuit_result.get('affected_campaigns', [])
                }
        
        return {'status': 'success', 'product_id': product_id}
    
    async def handle_product_deleted(
        self,
        store: StoreConnectionModel,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process product.deleted webhook (product removed).
        
        Actions:
        1. Mark product as inactive
        2. Pause all campaigns promoting this product
        """
        product_id = str(payload.get('id'))
        
        product = self.db.query(ProductModel).filter(
            ProductModel.store_id == store.id,
            ProductModel.platform_product_id == product_id
        ).first()
        
        if product:
            product.is_active = False
            product.in_stock = False
            self.db.commit()
            
            # Pause campaigns via SyncFlow™
            pause_result = await self.council.syncflow.pause_product_campaigns(
                store_id=store.id,
                product_id=product.id,
                platform_product_id=product_id,
                sku=product.sku or '',
                reason="product_deleted"
            )
            
            logger.warning(
                f"🗑️  Product {product_id} deleted, paused "
                f"{pause_result.get('campaigns_paused', 0)} campaigns"
            )
            
            return {
                'status': 'success',
                'product_id': product_id,
                'campaigns_paused': pause_result.get('campaigns_paused', 0)
            }
        
        return {'status': 'success', 'product_id': product_id, 'action': 'not_found'}
    
    # ========================================================================
    # Customer Webhooks
    # ========================================================================
    
    async def handle_customer_created(
        self,
        store: StoreConnectionModel,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process customer.created webhook (new customer signed up).
        
        Initialize customer in database for future LTV tracking.
        
        WooCommerce Payload:
        {
            "id": 101,
            "email": "customer@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "billing": {...},
            "total_spent": "0.00",
            "orders_count": 0
        }
        """
        customer_id = str(payload.get('id'))
        email = payload.get('email', '')
        
        # Create customer in database
        customer = CustomerModel(
            store_id=store.id,
            platform_customer_id=customer_id,
            email=email,
            first_name=payload.get('first_name', ''),
            last_name=payload.get('last_name', ''),
            phone=payload.get('billing', {}).get('phone', ''),
            total_orders=0,
            total_spent=Decimal('0.00'),
            synced_at=datetime.utcnow()
        )
        self.db.add(customer)
        self.db.commit()
        
        # Log to SyncShield™ for GDPR compliance
        await self.council.syncshield.log_data_access(
            action="create",
            resource_type="customer",
            resource_id=customer_id,
            user_id="system",
            metadata={'email': email, 'platform': 'woocommerce'}
        )
        
        logger.info(f"👤 New WooCommerce customer created: {email}")
        
        return {'status': 'success', 'customer_id': customer_id}
    
    async def handle_customer_updated(
        self,
        store: StoreConnectionModel,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process customer.updated webhook (customer info changed).
        
        Update customer profile and recalculate LTV if order count changed.
        """
        customer_id = str(payload.get('id'))
        email = payload.get('email', '')
        
        customer = self.db.query(CustomerModel).filter(
            CustomerModel.store_id == store.id,
            CustomerModel.platform_customer_id == customer_id
        ).first()
        
        if customer:
            old_total_spent = customer.total_spent
            new_total_spent = Decimal(str(payload.get('total_spent', '0.00')))
            
            customer.email = email
            customer.first_name = payload.get('first_name', '')
            customer.last_name = payload.get('last_name', '')
            customer.total_orders = payload.get('orders_count', 0)
            customer.total_spent = new_total_spent
            customer.synced_at = datetime.utcnow()
            
            self.db.commit()
            
            # If spending increased, update LTV prediction
            if new_total_spent > old_total_spent:
                order_amount = new_total_spent - old_total_spent
                
                await self.council.syncvalue.update_customer_ltv(
                    store_id=store.id,
                    customer_email=email,
                    order_amount=order_amount,
                    is_first_order=False,
                    order_date=datetime.utcnow()
                )
                
                logger.info(
                    f"📊 Updated LTV for {email} "
                    f"(new total spent: ${new_total_spent:.2f})"
                )
        
        return {'status': 'success', 'customer_id': customer_id}
