"""
CMS Platform Connectors for SyncPortal™

This package contains adapters for major e-commerce platforms.
Each connector implements a standard interface for:
- OAuth authentication
- Product catalog sync
- Order history retrieval
- Customer data sync
- Real-time webhook handling
- Inventory tracking

Supported Platforms:
- Shopify (OAuth2, GraphQL + REST)
- WooCommerce (API Keys, REST)
- Magento (OAuth1.0a, GraphQL + REST)
- BigCommerce (OAuth2, REST + GraphQL)
- Wix (OAuth2, REST)
- Squarespace (OAuth2, REST)
- PrestaShop (API Keys, REST)
- OpenCart (API Keys, REST)
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal


class BaseCMSConnector(ABC):
    """
    Abstract base class for all CMS platform connectors.
    
    All connectors must implement these methods to ensure
    compatibility with the SyncPortal™ orchestration layer.
    """
    
    def __init__(self, store_id: int, credentials: Dict[str, Any]):
        """
        Initialize connector with store credentials.
        
        Args:
            store_id: Database ID of the store connection
            credentials: Platform-specific auth credentials (access_token, etc.)
        """
        self.store_id = store_id
        self.credentials = credentials
        self.platform_name = self.__class__.__name__.replace("Connector", "").lower()
    
    # ========================================================================
    # OAuth & Authentication
    # ========================================================================
    
    @abstractmethod
    def verify_credentials(self) -> bool:
        """
        Verify that stored credentials are valid.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        pass
    
    @abstractmethod
    def refresh_token(self) -> Optional[str]:
        """
        Refresh OAuth access token if supported by platform.
        
        Returns:
            New access token or None if not supported
        """
        pass
    
    # ========================================================================
    # Product Catalog
    # ========================================================================
    
    @abstractmethod
    async def sync_products(
        self,
        limit: int = 250,
        page: int = 1,
        updated_since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch products from CMS platform.
        
        Args:
            limit: Number of products per page (max 250)
            page: Page number for pagination
            updated_since: Only fetch products updated after this timestamp
        
        Returns:
            List of product dictionaries with schema:
            {
                'platform_product_id': str,
                'sku': str,
                'title': str,
                'description': str,
                'price': Decimal,
                'inventory_quantity': int,
                'in_stock': bool,
                'image_url': str,
                'product_url': str,
                'images': List[str],
                'vendor': str,
                'product_type': str,
                'is_active': bool,
                'cost_per_item': Optional[Decimal],
                'compare_at_price': Optional[Decimal],
            }
        """
        pass
    
    @abstractmethod
    async def get_product_by_id(self, platform_product_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a single product by platform-specific ID.
        
        Args:
            platform_product_id: Platform's unique product identifier
        
        Returns:
            Product dictionary or None if not found
        """
        pass
    
    # ========================================================================
    # Order History
    # ========================================================================
    
    @abstractmethod
    async def sync_orders(
        self,
        limit: int = 250,
        page: int = 1,
        created_since: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch orders from CMS platform.
        
        Args:
            limit: Number of orders per page
            page: Page number for pagination
            created_since: Only fetch orders created after this timestamp
            status: Filter by order status (e.g., "paid", "fulfilled")
        
        Returns:
            List of order dictionaries with schema:
            {
                'platform_order_id': str,
                'order_number': str,
                'total_price': Decimal,
                'subtotal_price': Decimal,
                'total_tax': Decimal,
                'total_shipping': Decimal,
                'total_discounts': Decimal,
                'currency': str,
                'financial_status': str,
                'fulfillment_status': str,
                'order_date': datetime,
                'customer': {
                    'platform_customer_id': str,
                    'email': str,
                    'first_name': str,
                    'last_name': str,
                },
                'items': [
                    {
                        'platform_line_item_id': str,
                        'platform_product_id': str,
                        'sku': str,
                        'product_title': str,
                        'quantity': int,
                        'price': Decimal,
                        'total_price': Decimal,
                    }
                ],
            }
        """
        pass
    
    @abstractmethod
    async def get_order_by_id(self, platform_order_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a single order by platform-specific ID.
        
        Args:
            platform_order_id: Platform's unique order identifier
        
        Returns:
            Order dictionary or None if not found
        """
        pass
    
    # ========================================================================
    # Customer Data
    # ========================================================================
    
    @abstractmethod
    async def sync_customers(
        self,
        limit: int = 250,
        page: int = 1,
        updated_since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch customers from CMS platform.
        
        Args:
            limit: Number of customers per page
            page: Page number for pagination
            updated_since: Only fetch customers updated after this timestamp
        
        Returns:
            List of customer dictionaries with schema:
            {
                'platform_customer_id': str,
                'email': str,
                'first_name': str,
                'last_name': str,
                'phone': str,
                'total_orders': int,
                'total_spent': Decimal,
                'first_order_date': Optional[datetime],
                'last_order_date': Optional[datetime],
            }
        """
        pass
    
    # ========================================================================
    # Inventory Tracking
    # ========================================================================
    
    @abstractmethod
    async def get_inventory_level(self, platform_product_id: str) -> int:
        """
        Get current inventory level for a product.
        
        Args:
            platform_product_id: Platform's unique product identifier
        
        Returns:
            Current inventory quantity
        """
        pass
    
    @abstractmethod
    async def update_inventory(
        self,
        platform_product_id: str,
        quantity: int
    ) -> bool:
        """
        Update inventory level for a product (if write access granted).
        
        Args:
            platform_product_id: Platform's unique product identifier
            quantity: New inventory quantity
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    # ========================================================================
    # Webhook Management
    # ========================================================================
    
    @abstractmethod
    async def register_webhooks(self, webhook_url: str) -> List[str]:
        """
        Register webhooks for real-time data sync.
        
        Args:
            webhook_url: Public URL where webhooks will be received
        
        Returns:
            List of successfully registered webhook topics
        """
        pass
    
    @abstractmethod
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str
    ) -> bool:
        """
        Verify webhook authenticity using platform-specific signature.
        
        Args:
            payload: Raw webhook payload bytes
            signature: Signature from webhook headers
            secret: Webhook secret for verification
        
        Returns:
            True if signature is valid, False otherwise
        """
        pass
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    @abstractmethod
    async def get_store_info(self) -> Dict[str, Any]:
        """
        Get basic store information.
        
        Returns:
            {
                'store_name': str,
                'store_url': str,
                'email': str,
                'currency': str,
                'timezone': str,
                'plan': str,
            }
        """
        pass
    
    def calculate_baseline_metrics(
        self,
        orders: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate baseline metrics from historical orders.
        
        Args:
            orders: List of order dictionaries
            start_date: Start of baseline period
            end_date: End of baseline period
        
        Returns:
            {
                'total_revenue': Decimal,
                'total_orders': int,
                'avg_order_value': Decimal,
                'unique_customers': int,
                'repeat_customer_rate': float,
            }
        """
        total_revenue = Decimal("0.00")
        total_orders = len(orders)
        customer_ids = set()
        customer_order_counts = {}
        
        for order in orders:
            total_revenue += Decimal(str(order.get('total_price', 0)))
            customer_id = order.get('customer', {}).get('platform_customer_id')
            
            if customer_id:
                customer_ids.add(customer_id)
                customer_order_counts[customer_id] = customer_order_counts.get(customer_id, 0) + 1
        
        avg_order_value = total_revenue / total_orders if total_orders > 0 else Decimal("0.00")
        unique_customers = len(customer_ids)
        
        repeat_customers = sum(1 for count in customer_order_counts.values() if count > 1)
        repeat_customer_rate = (repeat_customers / unique_customers * 100) if unique_customers > 0 else 0.0
        
        return {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value,
            'unique_customers': unique_customers,
            'repeat_customer_rate': repeat_customer_rate,
            'baseline_start_date': start_date,
            'baseline_end_date': end_date,
        }
