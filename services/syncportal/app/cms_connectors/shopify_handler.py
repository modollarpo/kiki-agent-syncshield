"""
Shopify Webhook Handler for SyncPortal™

Processes real-time webhooks from Shopify CMS platform and coordinates
actions across the Council of Nine agents.

Webhook Topics Handled:
- orders/create → Attribution + SyncLedger + SyncEngage
- orders/paid → Trigger post-purchase flow
- products/update → Circuit breaker + SyncCreate refresh
- products/create → Generate ad creatives
- inventory_levels/update → Circuit breaker logic
- customers/create → Customer segmentation
- customers/update → Update LTV predictions

Architecture Flow:
    Shopify → Webhook → Verify HMAC → Log to SyncShield™ →
    Process Event → Notify Council Agents → Store in DB
"""
import hmac
import hashlib
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


class ShopifyWebhookHandler:
    """
    Handles all Shopify webhook events with Council of Nine integration.
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
        Verify Shopify HMAC-SHA256 webhook signature.
        
        Args:
            payload: Raw webhook payload bytes
            signature: X-Shopify-Hmac-Sha256 header value
            secret: Webhook secret from store connection
        
        Returns:
            True if signature is valid
        """
        computed_hmac = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(computed_hmac, signature)
    
    async def handle_webhook(
        self,
        topic: str,
        payload: Dict[str, Any],
        shop_domain: str,
        signature: str,
        raw_payload: bytes
    ) -> Dict[str, Any]:
        """
        Main webhook processing dispatcher.
        
        Args:
            topic: Webhook topic (e.g., "orders/create")
            payload: Parsed JSON payload
            shop_domain: Shopify shop domain
            signature: HMAC signature for verification
            raw_payload: Raw bytes for signature verification
        
        Returns:
            Processing result dictionary
        """
        # Find store connection
        store = self.db.query(StoreConnectionModel).filter(
            StoreConnectionModel.store_name == shop_domain,
            StoreConnectionModel.platform == 'shopify'
        ).first()
        
        if not store:
            logger.error(f"❌ Store not found: {shop_domain}")
            return {'status': 'error', 'message': 'Store not found'}
        
        # Verify webhook signature
        verified = self.verify_webhook_signature(
            raw_payload,
            signature,
            store.webhook_secret or ''
        )
        
        if not verified:
            logger.error(f"❌ Invalid webhook signature from {shop_domain}")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Log webhook to SyncShield™ for audit trail
        await self.council.syncshield.log_webhook_event(
            platform="shopify",
            topic=topic,
            payload_json=json.dumps(payload),
            signature=signature,
            verified=verified,
            store_id=store.id
        )
        
        # Route to appropriate handler
        handlers = {
            'orders/create': self.handle_order_created,
            'orders/paid': self.handle_order_paid,
            'orders/updated': self.handle_order_updated,
            'products/create': self.handle_product_created,
            'products/update': self.handle_product_updated,
            'products/delete': self.handle_product_deleted,
            'inventory_levels/update': self.handle_inventory_updated,
            'customers/create': self.handle_customer_created,
            'customers/update': self.handle_customer_updated,
        }
        
        handler = handlers.get(topic)
        if not handler:
            logger.warning(f"⚠️  No handler for topic: {topic}")
            return {'status': 'skipped', 'message': f'No handler for {topic}'}
        
        # Process webhook
        try:
            result = await handler(store, payload)
            logger.info(f"✅ Processed Shopify webhook: {topic} for {shop_domain}")
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
        Process orders/create webhook.
        
        Actions:
        1. Create order in database
        2. Run attribution engine
        3. Notify SyncLedger™ if incremental
        4. Update customer LTV in SyncValue™
        5. Trigger SyncEngage™ post-purchase flow
        """
        order_id = str(payload.get('id'))
        customer_data = payload.get('customer', {})
        total_price = Decimal(str(payload.get('total_price', '0.00')))
        
        # Use orchestrator to create order and run attribution
        result = await self.orchestrator.process_webhook(
            store_id=store.id,
            topic='orders/create',
            payload=payload
        )
        
        if not result.get('status') == 'success':
            return result
        
        # Get attribution result
        attribution = result.get('attribution', {})
        is_incremental = attribution.get('is_incremental', False)
        confidence = attribution.get('confidence', 0.0)
        
        # Update customer LTV in SyncValue™
        if customer_data.get('email'):
            ltv_result = await self.council.syncvalue.update_customer_ltv(
                store_id=store.id,
                customer_email=customer_data['email'],
                order_amount=total_price,
                is_first_order=payload.get('order_number') == '1',
                order_date=datetime.fromisoformat(payload['created_at'].replace('Z', '+00:00')),
                customer_data={
                    'platform_customer_id': str(customer_data.get('id', '')),
                    'first_name': customer_data.get('first_name', ''),
                    'last_name': customer_data.get('last_name', ''),
                    'total_orders': customer_data.get('orders_count', 1),
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
        if customer_data.get('email') and customer_data.get('accepts_marketing'):
            engage_result = await self.council.syncengage.trigger_post_purchase_flow(
                store_id=store.id,
                customer_data=customer_data,
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
            'engagement_triggered': bool(customer_data.get('accepts_marketing'))
        }
    
    async def handle_order_paid(
        self,
        store: StoreConnectionModel,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process orders/paid webhook (payment confirmed).
        
        This is a secondary confirmation that the order is financially settled.
        Update order status and potentially trigger additional flows.
        """
        order_id = str(payload.get('id'))
        
        # Update order financial status in database
        order = self.db.query(OrderModel).filter(
            OrderModel.store_id == store.id,
            OrderModel.platform_order_id == order_id
        ).first()
        
        if order:
            order.financial_status = 'paid'
            self.db.commit()
            
            logger.info(f"✅ Order {order_id} marked as paid")
        
        return {'status': 'success', 'order_id': order_id, 'action': 'status_updated'}
    
    async def handle_order_updated(
        self,
        store: StoreConnectionModel,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process orders/updated webhook (order modified).
        
        Handles refunds, cancellations, and order modifications.
        Important for OaaS accuracy - deduct refunded amounts.
        """
        order_id = str(payload.get('id'))
        financial_status = payload.get('financial_status')
        
        # Update order in database
        order = self.db.query(OrderModel).filter(
            OrderModel.store_id == store.id,
            OrderModel.platform_order_id == order_id
        ).first()
        
        if order:
            order.financial_status = financial_status
            
            # If refunded/cancelled, adjust incremental revenue
            if financial_status in ['refunded', 'partially_refunded', 'voided']:
                if order.is_incremental:
                    refund_amount = Decimal(str(payload.get('total_refunded', '0.00')))
                    
                    # Notify SyncLedger™ to deduct from OaaS calculation
                    # (This would need a new gRPC method: RecordRefund)
                    logger.warning(
                        f"⚠️  Order {order_id} refunded: ${refund_amount:.2f} "
                        f"(was incremental, adjusting OaaS)"
                    )
                    
                    order.incremental_revenue -= refund_amount
                    if order.incremental_revenue <= 0:
                        order.is_incremental = False
            
            self.db.commit()
        
        return {'status': 'success', 'order_id': order_id, 'financial_status': financial_status}
    
    # ========================================================================
    # Product Webhooks
    # ========================================================================
    
    async def handle_product_created(
        self,
        store: StoreConnectionModel,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process products/create webhook (new product added).
        
        Actions:
        1. Sync product to database
        2. Trigger SyncCreate™ to generate ad creatives
        3. Auto-create campaigns in SyncFlow™ (optional)
        """
        product_id = str(payload.get('id'))
        title = payload.get('title', '')
        
        # Sync product via connector
        connector = self.orchestrator.get_connector(store.id)
        if connector:
            product_data = await connector.get_product_by_id(product_id)
            
            if product_data:
                # Create product in database
                product = ProductModel(
                    store_id=store.id,
                    **product_data,
                    synced_at=datetime.utcnow()
                )
                self.db.add(product)
                self.db.commit()
                
                # Trigger SyncCreate™ to generate ad creatives
                creative_result = await self.council.synccreate.generate_product_creative(
                    store_id=store.id,
                    product_data=product_data,
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
        
        return {'status': 'error', 'message': 'Failed to sync product'}
    
    async def handle_product_updated(
        self,
        store: StoreConnectionModel,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process products/update webhook (product modified).
        
        Actions:
        1. Update product in database
        2. Check inventory changes for circuit breaker
        3. Refresh ad creatives in SyncCreate™ if images changed
        """
        product_id = str(payload.get('id'))
        
        # Find product in database
        product = self.db.query(ProductModel).filter(
            ProductModel.store_id == store.id,
            ProductModel.platform_product_id == product_id
        ).first()
        
        if product:
            old_inventory = product.inventory_quantity
            
            # Update product fields from webhook
            variant = payload.get('variants', [{}])[0]
            new_inventory = variant.get('inventory_quantity', 0)
            
            product.inventory_quantity = new_inventory
            product.in_stock = new_inventory > 0
            product.price = Decimal(str(variant.get('price', '0.00')))
            product.synced_at = datetime.utcnow()
            
            self.db.commit()
            
            # Check circuit breaker if inventory changed
            if old_inventory != new_inventory:
                circuit_result = await self.orchestrator.check_inventory_circuit_breaker(
                    product.id,
                    new_inventory
                )
                
                return {
                    'status': 'success',
                    'product_id': product_id,
                    'inventory_changed': True,
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
        Process products/delete webhook (product removed).
        
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
    
    async def handle_inventory_updated(
        self,
        store: StoreConnectionModel,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process inventory_levels/update webhook (CRITICAL FOR CIRCUIT BREAKER).
        
        This is the fastest way to detect out-of-stock events.
        """
        inventory_item_id = str(payload.get('inventory_item_id'))
        new_quantity = payload.get('available', 0)
        
        # Find product by inventory item ID (may need intermediate lookup)
        # For now, find by matching inventory in variants
        product = self.db.query(ProductModel).filter(
            ProductModel.store_id == store.id,
            # Would need additional field to map inventory_item_id to product
        ).first()
        
        if product:
            circuit_result = await self.orchestrator.check_inventory_circuit_breaker(
                product.id,
                new_quantity
            )
            
            return {
                'status': 'success',
                'inventory_item_id': inventory_item_id,
                'new_quantity': new_quantity,
                'circuit_breaker_action': circuit_result.get('action'),
                'affected_campaigns': circuit_result.get('affected_campaigns', [])
            }
        
        return {'status': 'success', 'inventory_item_id': inventory_item_id}
    
    # ========================================================================
    # Customer Webhooks
    # ========================================================================
    
    async def handle_customer_created(
        self,
        store: StoreConnectionModel,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process customers/create webhook (new customer signed up).
        
        Initialize customer in database for future LTV tracking.
        """
        customer_id = str(payload.get('id'))
        email = payload.get('email')
        
        # Create customer in database
        customer = CustomerModel(
            store_id=store.id,
            platform_customer_id=customer_id,
            email=email,
            first_name=payload.get('first_name', ''),
            last_name=payload.get('last_name', ''),
            phone=payload.get('phone', ''),
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
            metadata={'email': email, 'platform': 'shopify'}
        )
        
        logger.info(f"👤 New customer created: {email}")
        
        return {'status': 'success', 'customer_id': customer_id}
    
    async def handle_customer_updated(
        self,
        store: StoreConnectionModel,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process customers/update webhook (customer info changed).
        
        Update customer profile and recalculate LTV if order count changed.
        """
        customer_id = str(payload.get('id'))
        email = payload.get('email')
        
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
        
        return {'status': 'success', 'customer_id': customer_id}
