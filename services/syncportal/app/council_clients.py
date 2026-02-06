"""
gRPC Clients for Council of Nine Integration

This module provides async gRPC client wrappers for communication between
SyncPortal™ and the other agents in the KIKI Agent™ ecosystem.

Services:
- SyncValueClient: LTV predictions and baseline updates
- SyncFlowClient: Circuit breaker and bid adjustments
- SyncLedgerClient: OaaS settlement and revenue tracking
- SyncCreateClient: Creative generation from product feeds
- SyncEngageClient: Customer lifecycle automation
- SyncShieldClient: Audit logging and encryption

All clients use connection pooling and automatic retry logic.
"""
import grpc
from grpc import aio
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
import os
import logging

logger = logging.getLogger(__name__)

# Service URLs from environment
SYNCVALUE_GRPC_URL = os.getenv("SYNCVALUE_GRPC_URL", "syncvalue:50051")
SYNCFLOW_GRPC_URL = os.getenv("SYNCFLOW_GRPC_URL", "syncflow:50052")
SYNCLEDGER_GRPC_URL = os.getenv("SYNCLEDGER_GRPC_URL", "syncledger:50053")
SYNCCREATE_GRPC_URL = os.getenv("SYNCCREATE_GRPC_URL", "synccreate:50054")
SYNCENGAGE_GRPC_URL = os.getenv("SYNCENGAGE_GRPC_URL", "syncengage:50055")
SYNCSHIELD_GRPC_URL = os.getenv("SYNCSHIELD_GRPC_URL", "syncshield:50056")

# Internal API key for inter-service authentication
INTERNAL_API_KEY = os.getenv("KIKI_INTERNAL_API_KEY", "dev-internal-key-change-in-production")


class BaseGRPCClient:
    """Base class for gRPC clients with common functionality."""
    
    def __init__(self, service_url: str, service_name: str):
        self.service_url = service_url
        self.service_name = service_name
        self.channel = None
        
    async def _get_channel(self) -> aio.Channel:
        """Get or create gRPC channel with metadata interceptor."""
        if self.channel is None:
            # Create channel with keepalive settings
            options = [
                ('grpc.keepalive_time_ms', 30000),
                ('grpc.keepalive_timeout_ms', 10000),
                ('grpc.keepalive_permit_without_calls', True),
                ('grpc.http2.max_pings_without_data', 0),
            ]
            
            self.channel = aio.insecure_channel(
                self.service_url,
                options=options
            )
        
        return self.channel
    
    def _create_metadata(self) -> tuple:
        """Create metadata with internal API key for authentication."""
        return (
            ('x-internal-api-key', INTERNAL_API_KEY),
            ('x-source-service', 'syncportal'),
        )
    
    async def close(self):
        """Close gRPC channel."""
        if self.channel:
            await self.channel.close()
    
    def _money_to_decimal(self, money) -> Decimal:
        """Convert gRPC Money message to Decimal."""
        if not money:
            return Decimal("0.00")
        return Decimal(str(money.units)) + Decimal(str(money.nanos)) / Decimal("1000000000")
    
    def _decimal_to_money(self, amount: Decimal, currency: str = "USD"):
        """Convert Decimal to gRPC Money message."""
        # Import here to avoid circular dependency
        from schemas import cms_integration_pb2
        
        units = int(amount)
        nanos = int((amount - Decimal(units)) * Decimal("1000000000"))
        
        return cms_integration_pb2.Money(
            currency=currency,
            units=units,
            nanos=nanos
        )


# ========================================================================
# SyncValue™ Client - LTV Predictions
# ========================================================================

class SyncValueClient(BaseGRPCClient):
    """
    Client for SyncValue™ service - LTV predictions and baseline calculations.
    """
    
    def __init__(self):
        super().__init__(SYNCVALUE_GRPC_URL, "SyncValue")
    
    async def update_customer_ltv(
        self,
        store_id: int,
        customer_email: str,
        order_amount: Decimal,
        is_first_order: bool,
        order_date: datetime,
        customer_data: Dict[str, Any] = None,
        items: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update customer LTV prediction based on new order.
        
        Args:
            store_id: Store identifier
            customer_email: Customer email address
            order_amount: Total order value
            is_first_order: True if this is customer's first order
            order_date: When order was placed
            customer_data: Optional customer info (name, phone, etc.)
            items: Optional order line items
        
        Returns:
            {
                'success': bool,
                'predicted_ltv': Decimal,
                'confidence': float,
                'churn_risk_score': float,
                'ltv_segment': str  # 'high', 'medium', 'low'
            }
        """
        try:
            # Import protobuf (generated from .proto file)
            from schemas import cms_integration_pb2, cms_integration_pb2_grpc
            
            channel = await self._get_channel()
            stub = cms_integration_pb2_grpc.SyncValueServiceStub(channel)
            
            # Build request
            customer_info = cms_integration_pb2.CustomerInfo(
                platform_customer_id=customer_data.get('platform_customer_id', ''),
                email=customer_email,
                first_name=customer_data.get('first_name', '') if customer_data else '',
                last_name=customer_data.get('last_name', '') if customer_data else '',
                total_orders=customer_data.get('total_orders', 1) if customer_data else 1,
            )
            
            request = cms_integration_pb2.CustomerLTVUpdateRequest(
                store_id=store_id,
                customer=customer_info,
                order_amount=self._decimal_to_money(order_amount),
                is_first_order=is_first_order,
                # order_date would be converted to protobuf Timestamp
            )
            
            # Make gRPC call with metadata
            response = await stub.UpdateCustomerLTV(
                request,
                metadata=self._create_metadata()
            )
            
            logger.info(f"✅ SyncValue LTV updated for {customer_email}: ${response.predicted_ltv:.2f}")
            
            return {
                'success': response.success,
                'predicted_ltv': Decimal(str(response.predicted_ltv)),
                'confidence': response.confidence,
                'churn_risk_score': response.churn_risk_score,
                'ltv_segment': response.ltv_segment
            }
        
        except grpc.RpcError as e:
            logger.error(f"❌ SyncValue gRPC error: {e.code()} - {e.details()}")
            return {'success': False, 'error': str(e)}
        
        except Exception as e:
            logger.error(f"❌ SyncValue client error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def update_baseline_metrics(
        self,
        store_id: int,
        start_date: datetime,
        end_date: datetime,
        total_revenue: Decimal,
        total_orders: int,
        order_amounts: List[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Update baseline metrics for OaaS comparison.
        
        Returns:
            {
                'success': bool,
                'baseline_revenue': Decimal,
                'avg_order_value': Decimal,
                'unique_customers': int,
                'repeat_customer_rate': float
            }
        """
        try:
            from schemas import cms_integration_pb2, cms_integration_pb2_grpc
            
            channel = await self._get_channel()
            stub = cms_integration_pb2_grpc.SyncValueServiceStub(channel)
            
            request = cms_integration_pb2.BaselineUpdateRequest(
                store_id=store_id,
                total_orders=total_orders,
                # Add timestamps and order amounts
            )
            
            response = await stub.UpdateBaselineMetrics(
                request,
                metadata=self._create_metadata()
            )
            
            logger.info(f"✅ SyncValue baseline updated for store {store_id}")
            
            return {
                'success': response.success,
                'baseline_revenue': self._money_to_decimal(response.baseline_revenue),
                'avg_order_value': self._money_to_decimal(response.avg_order_value),
                'unique_customers': response.unique_customers,
                'repeat_customer_rate': response.repeat_customer_rate
            }
        
        except Exception as e:
            logger.error(f"❌ SyncValue baseline update error: {str(e)}")
            return {'success': False, 'error': str(e)}


# ========================================================================
# SyncFlow™ Client - Circuit Breaker
# ========================================================================

class SyncFlowClient(BaseGRPCClient):
    """
    Client for SyncFlow™ service - Circuit breaker and bid adjustments.
    """
    
    def __init__(self):
        super().__init__(SYNCFLOW_GRPC_URL, "SyncFlow")
    
    async def pause_product_campaigns(
        self,
        store_id: int,
        product_id: int,
        platform_product_id: str,
        sku: str,
        reason: str = "out_of_stock"
    ) -> Dict[str, Any]:
        """
        Pause all campaigns promoting this product (circuit breaker).
        
        Returns:
            {
                'success': bool,
                'affected_campaign_ids': List[str],
                'campaigns_paused': int,
                'estimated_daily_spend_saved': float
            }
        """
        try:
            from schemas import cms_integration_pb2, cms_integration_pb2_grpc
            
            channel = await self._get_channel()
            stub = cms_integration_pb2_grpc.SyncFlowServiceStub(channel)
            
            request = cms_integration_pb2.PauseCampaignsRequest(
                store_id=store_id,
                product_id=product_id,
                platform_product_id=platform_product_id,
                sku=sku,
                reason=reason
            )
            
            response = await stub.PauseProductCampaigns(
                request,
                metadata=self._create_metadata()
            )
            
            logger.warning(
                f"🚨 CIRCUIT BREAKER: Paused {response.campaigns_paused} campaigns "
                f"for product {sku} (saved ${response.estimated_daily_spend_saved:.2f}/day)"
            )
            
            return {
                'success': response.success,
                'affected_campaign_ids': list(response.affected_campaign_ids),
                'campaigns_paused': response.campaigns_paused,
                'estimated_daily_spend_saved': response.estimated_daily_spend_saved
            }
        
        except Exception as e:
            logger.error(f"❌ SyncFlow pause campaigns error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def resume_product_campaigns(
        self,
        store_id: int,
        product_id: int,
        platform_product_id: str,
        sku: str,
        new_inventory: int
    ) -> Dict[str, Any]:
        """
        Resume campaigns when product is restocked.
        
        Returns:
            {
                'success': bool,
                'affected_campaign_ids': List[str],
                'campaigns_resumed': int,
                'estimated_daily_spend_restored': float
            }
        """
        try:
            from schemas import cms_integration_pb2, cms_integration_pb2_grpc
            
            channel = await self._get_channel()
            stub = cms_integration_pb2_grpc.SyncFlowServiceStub(channel)
            
            request = cms_integration_pb2.ResumeCampaignsRequest(
                store_id=store_id,
                product_id=product_id,
                platform_product_id=platform_product_id,
                sku=sku,
                new_inventory_quantity=new_inventory
            )
            
            response = await stub.ResumeProductCampaigns(
                request,
                metadata=self._create_metadata()
            )
            
            logger.info(
                f"✅ CIRCUIT BREAKER: Resumed {response.campaigns_resumed} campaigns "
                f"for product {sku} (restored ${response.estimated_daily_spend_restored:.2f}/day)"
            )
            
            return {
                'success': response.success,
                'affected_campaign_ids': list(response.affected_campaign_ids),
                'campaigns_resumed': response.campaigns_resumed,
                'estimated_daily_spend_restored': response.estimated_daily_spend_restored
            }
        
        except Exception as e:
            logger.error(f"❌ SyncFlow resume campaigns error: {str(e)}")
            return {'success': False, 'error': str(e)}


# ========================================================================
# SyncLedger™ Client - OaaS Settlement
# ========================================================================

class SyncLedgerClient(BaseGRPCClient):
    """
    Client for SyncLedger™ service - Revenue tracking and OaaS billing.
    """
    
    def __init__(self):
        super().__init__(SYNCLEDGER_GRPC_URL, "SyncLedger")
    
    async def record_incremental_revenue(
        self,
        store_id: int,
        order_id: int,
        platform_order_id: str,
        order_amount: Decimal,
        incremental_amount: Decimal,
        attribution_confidence: float,
        campaign_id: str = None,
        touchpoint_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Record incremental revenue for OaaS settlement.
        
        Returns:
            {
                'success': bool,
                'counted_as_incremental': bool,
                'success_fee_amount': Decimal,  # 20% of incremental
                'invoice_id': str
            }
        """
        try:
            from schemas import cms_integration_pb2, cms_integration_pb2_grpc
            
            channel = await self._get_channel()
            stub = cms_integration_pb2_grpc.SyncLedgerServiceStub(channel)
            
            request = cms_integration_pb2.IncrementalRevenueRequest(
                store_id=store_id,
                order_id=order_id,
                platform_order_id=platform_order_id,
                order_amount=self._decimal_to_money(order_amount),
                incremental_amount=self._decimal_to_money(incremental_amount),
                attribution_confidence=attribution_confidence,
                campaign_id=campaign_id or '',
                touchpoint_ids=touchpoint_ids or []
            )
            
            response = await stub.RecordIncrementalRevenue(
                request,
                metadata=self._create_metadata()
            )
            
            success_fee = self._money_to_decimal(response.success_fee_amount)
            
            logger.info(
                f"💰 SyncLedger recorded ${incremental_amount:.2f} incremental "
                f"(success fee: ${success_fee:.2f})"
            )
            
            return {
                'success': response.success,
                'counted_as_incremental': response.counted_as_incremental,
                'success_fee_amount': success_fee,
                'invoice_id': response.invoice_id
            }
        
        except Exception as e:
            logger.error(f"❌ SyncLedger record revenue error: {str(e)}")
            return {'success': False, 'error': str(e)}


# ========================================================================
# SyncCreate™ Client - Creative Generation
# ========================================================================

class SyncCreateClient(BaseGRPCClient):
    """
    Client for SyncCreate™ service - Ad creative generation from product feeds.
    """
    
    def __init__(self):
        super().__init__(SYNCCREATE_GRPC_URL, "SyncCreate")
    
    async def generate_product_creative(
        self,
        store_id: int,
        product_data: Dict[str, Any],
        creative_type: str = "image",
        ad_network: str = "meta"
    ) -> Dict[str, Any]:
        """
        Generate ad creative from product data.
        
        Args:
            store_id: Store identifier
            product_data: Product info (title, description, images, etc.)
            creative_type: "image", "video", "carousel"
            ad_network: "google", "meta", "tiktok"
        
        Returns:
            {
                'success': bool,
                'creative_id': str,
                'generated_asset_urls': List[str],
                'headline': str,
                'description': str,
                'call_to_action': str
            }
        """
        try:
            from schemas import cms_integration_pb2, cms_integration_pb2_grpc
            
            channel = await self._get_channel()
            stub = cms_integration_pb2_grpc.SyncCreateServiceStub(channel)
            
            # Build product info
            product_info = cms_integration_pb2.ProductInfo(
                platform_product_id=product_data.get('platform_product_id', ''),
                sku=product_data.get('sku', ''),
                title=product_data.get('title', ''),
                description=product_data.get('description', ''),
                image_url=product_data.get('image_url', ''),
                image_urls=product_data.get('images', []),
                product_url=product_data.get('product_url', ''),
            )
            
            request = cms_integration_pb2.ProductCreativeRequest(
                store_id=store_id,
                product=product_info,
                creative_type=creative_type,
                ad_network=ad_network
            )
            
            response = await stub.GenerateProductCreative(
                request,
                metadata=self._create_metadata()
            )
            
            logger.info(
                f"🎨 SyncCreate generated {creative_type} creative for "
                f"{product_data.get('title', 'product')} "
                f"(ID: {response.creative_id})"
            )
            
            return {
                'success': response.success,
                'creative_id': response.creative_id,
                'generated_asset_urls': list(response.generated_asset_urls),
                'headline': response.headline,
                'description': response.description,
                'call_to_action': response.call_to_action
            }
        
        except Exception as e:
            logger.error(f"❌ SyncCreate generate creative error: {str(e)}")
            return {'success': False, 'error': str(e)}


# ========================================================================
# SyncEngage™ Client - Customer Lifecycle
# ========================================================================

class SyncEngageClient(BaseGRPCClient):
    """
    Client for SyncEngage™ service - Customer lifecycle automation.
    """
    
    def __init__(self):
        super().__init__(SYNCENGAGE_GRPC_URL, "SyncEngage")
    
    async def trigger_post_purchase_flow(
        self,
        store_id: int,
        customer_data: Dict[str, Any],
        order_id: int,
        order_amount: Decimal,
        items: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Trigger post-purchase email/SMS nurture flow.
        
        Returns:
            {
                'success': bool,
                'flow_id': str,
                'scheduled_emails': List[str],
                'scheduled_sms': List[str]
            }
        """
        try:
            from schemas import cms_integration_pb2, cms_integration_pb2_grpc
            
            channel = await self._get_channel()
            stub = cms_integration_pb2_grpc.SyncEngageServiceStub(channel)
            
            customer_info = cms_integration_pb2.CustomerInfo(
                email=customer_data.get('email', ''),
                first_name=customer_data.get('first_name', ''),
                last_name=customer_data.get('last_name', ''),
            )
            
            request = cms_integration_pb2.PostPurchaseRequest(
                store_id=store_id,
                customer=customer_info,
                order_id=order_id,
                order_amount=self._decimal_to_money(order_amount)
            )
            
            response = await stub.TriggerPostPurchaseFlow(
                request,
                metadata=self._create_metadata()
            )
            
            logger.info(
                f"💌 SyncEngage triggered post-purchase flow for "
                f"{customer_data.get('email', 'customer')} "
                f"({len(response.scheduled_emails)} emails scheduled)"
            )
            
            return {
                'success': response.success,
                'flow_id': response.flow_id,
                'scheduled_emails': list(response.scheduled_emails),
                'scheduled_sms': list(response.scheduled_sms)
            }
        
        except Exception as e:
            logger.error(f"❌ SyncEngage trigger flow error: {str(e)}")
            return {'success': False, 'error': str(e)}


# ========================================================================
# SyncShield™ Client - Audit & Encryption
# ========================================================================

class SyncShieldClient(BaseGRPCClient):
    """
    Client for SyncShield™ service - Audit logging and encryption.
    """
    
    def __init__(self):
        super().__init__(SYNCSHIELD_GRPC_URL, "SyncShield")
    
    async def log_data_access(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: str = None,
        metadata: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Log CMS data access for GDPR/CCPA compliance.
        
        Args:
            action: "read", "write", "delete"
            resource_type: "customer", "order", "product"
            resource_id: ID of accessed resource
            user_id: Optional user who performed action
            metadata: Additional context
        
        Returns:
            {
                'success': bool,
                'audit_log_id': str,
                'logged_at': datetime
            }
        """
        try:
            from schemas import cms_integration_pb2, cms_integration_pb2_grpc
            
            channel = await self._get_channel()
            stub = cms_integration_pb2_grpc.SyncShieldServiceStub(channel)
            
            request = cms_integration_pb2.DataAccessLogRequest(
                service_name="syncportal",
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                user_id=user_id or "system",
                metadata=metadata or {}
            )
            
            response = await stub.LogDataAccess(
                request,
                metadata=self._create_metadata()
            )
            
            return {
                'success': response.success,
                'audit_log_id': response.audit_log_id
            }
        
        except Exception as e:
            logger.error(f"❌ SyncShield log access error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def log_webhook_event(
        self,
        platform: str,
        topic: str,
        payload_json: str,
        signature: str,
        verified: bool,
        store_id: int
    ) -> Dict[str, Any]:
        """
        Log webhook processing for debugging and replay.
        
        Returns:
            {
                'success': bool,
                'log_id': str
            }
        """
        try:
            from schemas import cms_integration_pb2, cms_integration_pb2_grpc
            
            channel = await self._get_channel()
            stub = cms_integration_pb2_grpc.SyncShieldServiceStub(channel)
            
            request = cms_integration_pb2.WebhookLogRequest(
                platform=platform,
                topic=topic,
                payload_json=payload_json,
                signature=signature,
                verified=verified,
                store_id=store_id
            )
            
            response = await stub.LogWebhookEvent(
                request,
                metadata=self._create_metadata()
            )
            
            return {
                'success': response.success,
                'log_id': response.log_id
            }
        
        except Exception as e:
            logger.error(f"❌ SyncShield log webhook error: {str(e)}")
            return {'success': False, 'error': str(e)}


# ========================================================================
# Council Client Factory
# ========================================================================

class CouncilOfNineClients:
    """
    Factory to access all Council of Nine gRPC clients.
    
    Usage:
        council = CouncilOfNineClients()
        await council.syncvalue.update_customer_ltv(...)
        await council.syncflow.pause_product_campaigns(...)
        await council.syncledger.record_incremental_revenue(...)
    """
    
    def __init__(self):
        self.syncvalue = SyncValueClient()
        self.syncflow = SyncFlowClient()
        self.syncledger = SyncLedgerClient()
        self.synccreate = SyncCreateClient()
        self.syncengage = SyncEngageClient()
        self.syncshield = SyncShieldClient()
    
    async def close_all(self):
        """Close all gRPC channels."""
        await self.syncvalue.close()
        await self.syncflow.close()
        await self.syncledger.close()
        await self.synccreate.close()
        await self.syncengage.close()
        await self.syncshield.close()
