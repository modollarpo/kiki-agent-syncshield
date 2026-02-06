"""
CMS Integration Orchestrator for SyncPortal™

This module coordinates the closed-loop revenue engine by integrating:
- CMS platform connectors (Shopify, WooCommerce, BigCommerce, etc.)
- Real-time webhook processing
- Attribution engine for OaaS verification
- Inventory circuit breaker
- Integration with Council of Nine agents

Architecture:
    CMS Webhook → SyncPortal → Attribution Engine → Update Database
                              → Circuit Breaker → Pause/Resume Campaigns
                              → Trigger SyncEngage™ flows
                              → Update SyncValue™ predictions
                              → SyncLedger™ settlement calculations
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import httpx
import logging

from shared.ecommerce_models import (
    StoreConnectionModel,
    ProductModel,
    OrderModel,
    OrderItemModel,
    CustomerModel,
    InventoryEventModel,
    WebhookLogModel,
)
from .connectors import BaseCMSConnector
from .connectors.shopify import ShopifyConnector
from .connectors.woocommerce import WooCommerceConnector
from .connectors.bigcommerce import BigCommerceConnector
from .council_clients import CouncilOfNineClients

logger = logging.getLogger(__name__)


class CMSIntegrationOrchestrator:
    """
    Coordinates all CMS integration activities including sync, attribution, and circuit breaker.
    """
    
    # Platform connector mapping
    CONNECTOR_MAP = {
        'shopify': ShopifyConnector,
        'woocommerce': WooCommerceConnector,
        'bigcommerce': BigCommerceConnector,
        # Add more as implemented: 'magento': MagentoConnector, etc.
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.council = CouncilOfNineClients()  # gRPC clients for Council of Nine
    
    # ========================================================================
    # Connector Factory
    # ========================================================================
    
    def get_connector(self, store_id: int) -> Optional[BaseCMSConnector]:
        """
        Get platform-specific connector for a store.
        
        Args:
            store_id: Database ID of store connection
        
        Returns:
            Connector instance or None if store not found
        """
        store = self.db.query(StoreConnectionModel).filter(
            StoreConnectionModel.id == store_id
        ).first()
        
        if not store or not store.sync_enabled:
            return None
        
        connector_class = self.CONNECTOR_MAP.get(store.platform.lower())
        if not connector_class:
            logger.error(f"No connector found for platform: {store.platform}")
            return None
        
        credentials = {
            'access_token': store.access_token,
            'refresh_token': store.refresh_token,
            'shop_domain': store.store_name if store.platform == 'shopify' else None,
            'site_url': store.site_url if store.platform == 'woocommerce' else None,
            'store_hash': store.shop_id if store.platform == 'bigcommerce' else None,
            'consumer_key': store.access_token if store.platform == 'woocommerce' else None,
            'consumer_secret': store.refresh_token if store.platform == 'woocommerce' else None,
        }
        
        return connector_class(store_id=store.id, credentials=credentials)
    
    # ========================================================================
    # Historical Baseline Calculation
    # ========================================================================
    
    async def calculate_baseline(
        self,
        store_id: int,
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Calculate pre-KIKI historical baseline metrics.
        
        This establishes the "before" state for OaaS uplift calculations.
        
        Args:
            store_id: Store to analyze
            months: Number of months to analyze (default 12)
        
        Returns:
            Baseline metrics dictionary
        """
        connector = self.get_connector(store_id)
        if not connector:
            raise ValueError(f"Store {store_id} not found or disabled")
        
        store = self.db.query(StoreConnectionModel).get(store_id)
        
        # Define baseline period (12 months before KIKI integration)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)
        
        logger.info(f"Calculating baseline for store {store_id}: {start_date} to {end_date}")
        
        # Fetch all orders in baseline period
        all_orders = []
        page = 1
        
        while True:
            orders = await connector.sync_orders(
                limit=250,
                page=page,
                created_since=start_date
            )
            
            if not orders:
                break
            
            # Only include orders before KIKI integration
            baseline_orders = [
                o for o in orders
                if o['order_date'] < store.connected_at
            ]
            
            all_orders.extend(baseline_orders)
            page += 1
            
            if len(orders) < 250:  # Last page
                break
        
        # Calculate baseline metrics
        metrics = connector.calculate_baseline_metrics(
            orders=all_orders,
            start_date=start_date,
            end_date=end_date
        )
        
        # Update store with baseline data
        store.baseline_start_date = start_date
        store.baseline_end_date = end_date
        store.baseline_revenue = metrics['total_revenue']
        store.baseline_order_count = metrics['total_orders']
        store.baseline_avg_order_value = metrics['avg_order_value']
        
        self.db.commit()
        
        logger.info(f"Baseline calculated: ${metrics['total_revenue']} from {metrics['total_orders']} orders")
        
        return metrics
    
    # ========================================================================
    # Product Sync
    # ========================================================================
    
    async def sync_products(self, store_id: int) -> int:
        """
        Sync product catalog from CMS to database.
        
        This enables SyncCreate™ to pull product images/descriptions for creative generation.
        
        Args:
            store_id: Store to sync
        
        Returns:
            Number of products synced
        """
        connector = self.get_connector(store_id)
        if not connector:
            raise ValueError(f"Store {store_id} not found")
        
        store = self.db.query(StoreConnectionModel).get(store_id)
        
        synced_count = 0
        page = 1
        
        while True:
            products = await connector.sync_products(
                limit=250,
                page=page,
                updated_since=store.last_product_sync
            )
            
            if not products:
                break
            
            for product_data in products:
                # Upsert product
                product = self.db.query(ProductModel).filter(
                    and_(
                        ProductModel.store_id == store_id,
                        ProductModel.platform_product_id == product_data['platform_product_id']
                    )
                ).first()
                
                if product:
                    # Update existing
                    for key, value in product_data.items():
                        setattr(product, key, value)
                    product.synced_at = datetime.utcnow()
                else:
                    # Create new
                    product = ProductModel(
                        store_id=store_id,
                        **product_data,
                        synced_at=datetime.utcnow()
                    )
                    self.db.add(product)
                
                synced_count += 1
            
            self.db.commit()
            page += 1
            
            if len(products) < 250:
                break
        
        # Update store sync timestamp
        store.last_product_sync = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Synced {synced_count} products for store {store_id}")
        
        return synced_count
    
    # ========================================================================
    # Order Attribution Engine
    # ========================================================================
    
    async def attribute_order(
        self,
        order_id: int,
        customer_email: str,
        order_date: datetime
    ) -> Dict[str, Any]:
        """
        Determine if an order should be attributed to KIKI for OaaS settlement.
        
        Attribution Logic:
        1. Check if customer touched a KIKI ad in last 30 days
        2. Check if order contains products from active KIKI campaigns
        3. Calculate attribution confidence (0.0 - 1.0)
        4. Mark as incremental if confidence > 0.7
        
        Args:
            order_id: Database ID of order
            customer_email: Customer email for matching
            order_date: When order was placed
        
        Returns:
            Attribution result with confidence score
        """
        order = self.db.query(OrderModel).get(order_id)
        if not order:
            return {'attributed_to_kiki': False, 'confidence': 0.0}
        
        # Check if customer interacted with KIKI ads
        # This queries SyncFlow™'s click/impression tracking
        touchpoint_window = order_date - timedelta(days=30)
        
        # Pseudo-code (requires SyncFlow integration):
        # touchpoints = query_syncflow_touchpoints(
        #     email=customer_email,
        #     start_date=touchpoint_window,
        #     end_date=order_date
        # )
        
        # For now, use simplified logic based on campaign_id in order metadata
        attributed_to_kiki = False
        confidence = 0.0
        campaign_id = None
        touchpoint_ids = []
        
        # Check if any order items match active KIKI campaigns
        for item in order.items:
            product = item.product
            if product and product.ltv_category_weight > 1.0:
                # This product was being promoted by KIKI
                confidence += 0.3
                attributed_to_kiki = True
        
        # Check if customer was acquired via KIKI
        customer = order.customer
        if customer and customer.acquired_via_kiki:
            confidence += 0.5
            campaign_id = customer.acquisition_campaign_id
            attributed_to_kiki = True
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        # Mark as incremental if confidence > 0.7
        is_incremental = confidence >= 0.7
        
        # Update order attribution
        order.attributed_to_kiki = attributed_to_kiki
        order.attribution_confidence = confidence
        order.campaign_id = campaign_id
        order.touchpoint_ids = touchpoint_ids
        order.is_incremental = is_incremental
        
        if is_incremental:
            order.incremental_revenue = order.total_price
        
        self.db.commit()
        
        logger.info(f"Order {order_id} attribution: {attributed_to_kiki} (confidence: {confidence:.2f})")
        
        # Notify SyncLedger™ for OaaS settlement calculation
        if is_incremental:
            await self._notify_syncledger(order_id, order.incremental_revenue)
        
        return {
            'attributed_to_kiki': attributed_to_kiki,
            'confidence': confidence,
            'is_incremental': is_incremental,
            'incremental_revenue': order.incremental_revenue,
            'campaign_id': campaign_id
        }
    
    # ========================================================================
    # Inventory Circuit Breaker
    # ========================================================================
    
    async def check_inventory_circuit_breaker(
        self,
        product_id: int,
        new_quantity: int
    ) -> Dict[str, Any]:
        """
        Check if inventory change triggers circuit breaker to pause/resume ads.
        
        Circuit Breaker Logic:
        - If inventory drops to 0 → Pause all campaigns promoting this product
        - If inventory restocked → Resume paused campaigns
        - If inventory below threshold → Reduce bids by 50% (optional)
        
        Args:
            product_id: Database ID of product
            new_quantity: New inventory level
        
        Returns:
            Circuit breaker action result
        """
        product = self.db.query(ProductModel).get(product_id)
        if not product:
            return {'action': 'none', 'reason': 'product_not_found'}
        
        previous_quantity = product.inventory_quantity
        product.inventory_quantity = new_quantity
        product.in_stock = new_quantity > 0
        
        # Log inventory event
        event = InventoryEventModel(
            product_id=product_id,
            event_type='out_of_stock' if new_quantity == 0 else ('low_stock' if new_quantity < product.low_stock_threshold else 'restock'),
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            quantity_change=new_quantity - previous_quantity,
            occurred_at=datetime.utcnow()
        )
        self.db.add(event)
        
        action_taken = 'none'
        affected_campaigns = []
        
        # Trigger circuit breaker if configured
        if product.auto_pause_ads:
            if new_quantity == 0 and previous_quantity > 0:
                # OUT OF STOCK - PAUSE ADS
                action_taken = 'pause_campaigns'
                affected_campaigns = await self._pause_product_campaigns(product_id)
                event.triggered_ad_pause = True
                event.affected_campaign_ids = affected_campaigns
                
                logger.warning(f"🚨 Circuit Breaker: Product {product_id} OUT OF STOCK - Paused {len(affected_campaigns)} campaigns")
            
            elif new_quantity > 0 and previous_quantity == 0:
                # RESTOCKED - RESUME ADS
                action_taken = 'resume_campaigns'
                affected_campaigns = await self._resume_product_campaigns(product_id)
                event.triggered_ad_resume = True
                event.affected_campaign_ids = affected_campaigns
                
                logger.info(f"✅ Circuit Breaker: Product {product_id} RESTOCKED - Resumed {len(affected_campaigns)} campaigns")
        
        self.db.commit()
        
        return {
            'action': action_taken,
            'product_id': product_id,
            'new_quantity': new_quantity,
            'previous_quantity': previous_quantity,
            'affected_campaigns': affected_campaigns
        }
    
    async def _pause_product_campaigns(self, product_id: int) -> List[str]:
        """Pause SyncFlow™ campaigns promoting this product."""
        # Get product details from database
        product = self.db.query(ProductModel).get(product_id)
        if not product:
            logger.warning(f"Product {product_id} not found for campaign pause")
            return []
        
        # Call SyncFlow™ via gRPC
        result = await self.council.syncflow.pause_product_campaigns(
            store_id=product.store_id,
            product_id=product_id,
            platform_product_id=product.platform_product_id,
            sku=product.sku or '',
            reason="out_of_stock"
        )
        
        if result.get('success'):
            return result.get('affected_campaign_ids', [])
        else:
            logger.error(f"Failed to pause campaigns: {result.get('error')}")
            return []
    
    async def _resume_product_campaigns(self, product_id: int) -> List[str]:
        """Resume SyncFlow™ campaigns for restocked product."""
        # Get product details from database
        product = self.db.query(ProductModel).get(product_id)
        if not product:
            logger.warning(f"Product {product_id} not found for campaign resume")
            return []
        
        # Call SyncFlow™ via gRPC
        result = await self.council.syncflow.resume_product_campaigns(
            store_id=product.store_id,
            product_id=product_id,
            platform_product_id=product.platform_product_id,
            sku=product.sku or '',
        )
        
        if result.get('success'):
            return result.get('affected_campaign_ids', [])
        else:
            logger.error(f"Failed to resume campaigns: {result.get('error')}")
            return []
    
    # ========================================================================
    # Webhook Processing
    # ========================================================================
    
    async def process_webhook(
        self,
        store_id: int,
        topic: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process incoming CMS webhook for real-time updates.
        
        Webhook Topics:
        - products/update → Update product inventory, trigger circuit breaker
        - orders/create → Create order record, run attribution engine
        - orders/paid → Trigger SyncEngage™ post-purchase flow
        - inventory/update → Check circuit breaker
        
        Args:
            store_id: Store that sent webhook
            topic: Webhook topic (e.g., "orders/create")
            payload: Webhook payload data
        
        Returns:
            Processing result
        """
        store = self.db.query(StoreConnectionModel).get(store_id)
        if not store:
            return {'status': 'error', 'message': 'Store not found'}
        
        connector = self.get_connector(store_id)
        if not connector:
            return {'status': 'error', 'message': 'Connector not available'}
        
        result = {'status': 'success', 'topic': topic}
        
        try:
            if 'product' in topic and 'update' in topic:
                # Product updated - check inventory
                product_id = payload.get('id')
                if product_id:
                    product_data = await connector.get_product_by_id(str(product_id))
                    
                    if product_data:
                        # Update database
                        db_product = self.db.query(ProductModel).filter(
                            and_(
                                ProductModel.store_id == store_id,
                                ProductModel.platform_product_id == str(product_id)
                            )
                        ).first()
                        
                        if db_product:
                            old_qty = db_product.inventory_quantity
                            new_qty = product_data['inventory_quantity']
                            
                            # Update product
                            for key, value in product_data.items():
                                setattr(db_product, key, value)
                            
                            self.db.commit()
                            
                            # Check circuit breaker
                            if old_qty != new_qty:
                                cb_result = await self.check_inventory_circuit_breaker(
                                    db_product.id,
                                    new_qty
                                )
                                result['circuit_breaker'] = cb_result
            
            elif 'order' in topic and 'create' in topic:
                # New order - create record and run attribution
                order_id = payload.get('id')
                if order_id:
                    order_data = await connector.get_order_by_id(str(order_id))
                    
                    if order_data:
                        # Create order in database
                        customer_data = order_data['customer']
                        
                        # Find or create customer
                        customer = self.db.query(CustomerModel).filter(
                            and_(
                                CustomerModel.store_id == store_id,
                                CustomerModel.platform_customer_id == customer_data['platform_customer_id']
                            )
                        ).first()
                        
                        if not customer and customer_data['email']:
                            customer = CustomerModel(
                                store_id=store_id,
                                platform_customer_id=customer_data['platform_customer_id'],
                                email=customer_data['email'],
                                first_name=customer_data['first_name'],
                                last_name=customer_data['last_name']
                            )
                            self.db.add(customer)
                            self.db.flush()
                        
                        # Create order
                        order = OrderModel(
                            store_id=store_id,
                            customer_id=customer.id if customer else None,
                            platform_order_id=order_data['platform_order_id'],
                            order_number=order_data['order_number'],
                            total_price=order_data['total_price'],
                            subtotal_price=order_data['subtotal_price'],
                            total_tax=order_data['total_tax'],
                            total_shipping=order_data['total_shipping'],
                            total_discounts=order_data['total_discounts'],
                            currency=order_data['currency'],
                            financial_status=order_data['financial_status'],
                            fulfillment_status=order_data['fulfillment_status'],
                            order_date=order_data['order_date']
                        )
                        self.db.add(order)
                        self.db.flush()
                        
                        # Create order items
                        for item_data in order_data['items']:
                            # Find product
                            product = self.db.query(ProductModel).filter(
                                and_(
                                    ProductModel.store_id == store_id,
                                    ProductModel.platform_product_id == item_data['platform_product_id']
                                )
                            ).first()
                            
                            item = OrderItemModel(
                                order_id=order.id,
                                product_id=product.id if product else None,
                                platform_line_item_id=item_data['platform_line_item_id'],
                                platform_product_id=item_data['platform_product_id'],
                                sku=item_data['sku'],
                                product_title=item_data['product_title'],
                                quantity=item_data['quantity'],
                                price=item_data['price'],
                                total_price=item_data['total_price']
                            )
                            self.db.add(item)
                        
                        self.db.commit()
                        
                        # Run attribution engine
                        attribution = await self.attribute_order(
                            order.id,
                            customer.email if customer else '',
                            order.order_date
                        )
                        result['attribution'] = attribution
                        
                        # Trigger SyncEngage™ post-purchase flow
                        if customer and customer.opted_in_email:
                            await self._trigger_syncengage_flow(
                                customer_id=customer.id,
                                flow_type='post_purchase',
                                order_id=order.id
                            )
            
            return result
        
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    # ========================================================================
    # Integration with Council of Nine
    # ========================================================================
    
    async def _notify_syncledger(self, order_id: int, incremental_revenue: Decimal):
        """Notify SyncLedger™ of incremental revenue for OaaS settlement."""
        # Get order details from database
        order = self.db.query(OrderModel).get(order_id)
        if not order:
            logger.warning(f"Order {order_id} not found for SyncLedger notification")
            return
        
        # Call SyncLedger™ via gRPC
        result = await self.council.syncledger.record_incremental_revenue(
            store_id=order.store_id,
            order_id=order_id,
            platform_order_id=order.platform_order_id,
            order_amount=order.total_price,
            incremental_amount=incremental_revenue,
            attribution_confidence=order.attribution_confidence or 0.0,
            campaign_id=order.campaign_id,
            touchpoint_ids=[]  # TODO: Extract from attribution data
        )
        
        if result.get('success'):
            logger.info(
                f"💰 SyncLedger recorded ${incremental_revenue:.2f} incremental "
                f"(fee: ${result.get('success_fee_amount', 0):.2f})"
            )
        else:
            logger.error(f"Failed to notify SyncLedger: {result.get('error')}")
    
    async def _trigger_syncengage_flow(
        self,
        customer_id: int,
        flow_type: str,
        order_id: int
    ):
        """Trigger SyncEngage™ retention flow (email/SMS nurture)."""
        # Get customer and order details from database
        customer = self.db.query(CustomerModel).get(customer_id)
        order = self.db.query(OrderModel).get(order_id)
        
        if not customer or not order:
            logger.warning(f"Customer {customer_id} or order {order_id} not found for SyncEngage")
            return
        
        # Get order items for personalization
        items = self.db.query(OrderItemModel).filter(
            OrderItemModel.order_id == order_id
        ).all()
        
        item_data = [{
            'product_id': item.platform_product_id,
            'title': item.product_title,
            'quantity': item.quantity,
            'price': float(item.price)
        } for item in items]
        
        # Call SyncEngage™ via gRPC
        result = await self.council.syncengage.trigger_post_purchase_flow(
            store_id=order.store_id,
            customer_data={
                'email': customer.email,
                'first_name': customer.first_name or '',
                'last_name': customer.last_name or '',
            },
            order_id=order_id,
            order_amount=order.total_price,
            items=item_data
        )
        
        if result.get('success'):
            logger.info(
                f"💌 SyncEngage triggered {flow_type} flow: {result.get('flow_id')} "
                f"({len(result.get('scheduled_emails', []))} emails scheduled)"
            )
        else:
            logger.error(f"Failed to trigger SyncEngage flow: {result.get('error')}")
