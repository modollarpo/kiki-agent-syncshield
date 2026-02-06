"""
WooCommerce Connector for SyncPortal™

Implements REST API integration with WooCommerce (WordPress plugin).

WooCommerce REST API Documentation:
- https://woocommerce.github.io/woocommerce-rest-api-docs/

Authentication:
- Uses Consumer Key + Consumer Secret (generated in WooCommerce admin)
- Supports OAuth1.0a or Basic Auth over HTTPS

Required Permissions:
- Read access to products, orders, customers
- Optional write access to inventory levels
"""
import hmac
import hashlib
import base64
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
from . import BaseCMSConnector


class WooCommerceConnector(BaseCMSConnector):
    """
    WooCommerce platform connector using REST API v3.
    """
    
    API_VERSION = "wc/v3"
    
    def __init__(self, store_id: int, credentials: Dict[str, Any]):
        super().__init__(store_id, credentials)
        self.site_url = credentials.get('site_url')  # e.g., "https://example.com"
        self.consumer_key = credentials.get('consumer_key')
        self.consumer_secret = credentials.get('consumer_secret')
        self.api_base = f"{self.site_url}/wp-json/{self.API_VERSION}"
        
        # WooCommerce uses Basic Auth with consumer key/secret
        auth_string = f"{self.consumer_key}:{self.consumer_secret}"
        auth_bytes = base64.b64encode(auth_string.encode('utf-8'))
        
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Basic {auth_bytes.decode('utf-8')}",
                "Content-Type": "application/json",
            },
            timeout=30.0
        )
    
    # ========================================================================
    # OAuth & Authentication
    # ========================================================================
    
    def verify_credentials(self) -> bool:
        """Verify WooCommerce API credentials."""
        try:
            response = httpx.get(
                f"{self.api_base}/system_status",
                headers=self.client.headers
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def refresh_token(self) -> Optional[str]:
        """WooCommerce uses static API keys, no refresh needed."""
        return None
    
    # ========================================================================
    # Product Catalog
    # ========================================================================
    
    async def sync_products(
        self,
        limit: int = 100,
        page: int = 1,
        updated_since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch products from WooCommerce."""
        params = {
            "per_page": min(limit, 100),  # WooCommerce max is 100
            "page": page,
            "status": "publish"
        }
        
        if updated_since:
            params["after"] = updated_since.isoformat()
        
        response = await self.client.get(f"{self.api_base}/products", params=params)
        response.raise_for_status()
        
        products_data = response.json()
        products = []
        
        for product in products_data:
            # WooCommerce has product types, use regular/simple products
            products.append({
                'platform_product_id': str(product['id']),
                'sku': product.get('sku', ''),
                'title': product.get('name', ''),
                'description': product.get('description', ''),
                'price': Decimal(str(product.get('price', '0.00'))),
                'inventory_quantity': product.get('stock_quantity', 0) or 0,
                'in_stock': product.get('stock_status') == 'instock',
                'image_url': product.get('images', [{}])[0].get('src', '') if product.get('images') else '',
                'product_url': product.get('permalink', ''),
                'images': [img['src'] for img in product.get('images', [])],
                'vendor': '',  # WooCommerce doesn't have built-in vendor field
                'product_type': ', '.join([cat['name'] for cat in product.get('categories', [])]),
                'is_active': product.get('status') == 'publish',
                'cost_per_item': None,  # Not available in standard WooCommerce
                'compare_at_price': Decimal(str(product.get('regular_price', '0.00'))) if product.get('sale_price') else None,
            })
        
        return products
    
    async def get_product_by_id(self, platform_product_id: str) -> Optional[Dict[str, Any]]:
        """Fetch single WooCommerce product."""
        try:
            response = await self.client.get(f"{self.api_base}/products/{platform_product_id}")
            response.raise_for_status()
            
            product = response.json()
            
            return {
                'platform_product_id': str(product['id']),
                'sku': product.get('sku', ''),
                'title': product.get('name', ''),
                'description': product.get('description', ''),
                'price': Decimal(str(product.get('price', '0.00'))),
                'inventory_quantity': product.get('stock_quantity', 0) or 0,
                'in_stock': product.get('stock_status') == 'instock',
                'image_url': product.get('images', [{}])[0].get('src', '') if product.get('images') else '',
                'product_url': product.get('permalink', ''),
                'images': [img['src'] for img in product.get('images', [])],
                'vendor': '',
                'product_type': ', '.join([cat['name'] for cat in product.get('categories', [])]),
                'is_active': product.get('status') == 'publish',
            }
        except httpx.HTTPStatusError:
            return None
    
    # ========================================================================
    # Order History
    # ========================================================================
    
    async def sync_orders(
        self,
        limit: int = 100,
        page: int = 1,
        created_since: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch orders from WooCommerce."""
        params = {
            "per_page": min(limit, 100),
            "page": page,
        }
        
        if status:
            params["status"] = status
        
        if created_since:
            params["after"] = created_since.isoformat()
        
        response = await self.client.get(f"{self.api_base}/orders", params=params)
        response.raise_for_status()
        
        orders_data = response.json()
        orders = []
        
        for order in orders_data:
            billing = order.get('billing', {})
            
            orders.append({
                'platform_order_id': str(order['id']),
                'order_number': str(order.get('number', '')),
                'total_price': Decimal(str(order.get('total', '0.00'))),
                'subtotal_price': Decimal(str(sum(Decimal(item['subtotal']) for item in order.get('line_items', [])))),
                'total_tax': Decimal(str(order.get('total_tax', '0.00'))),
                'total_shipping': Decimal(str(order.get('shipping_total', '0.00'))),
                'total_discounts': Decimal(str(order.get('discount_total', '0.00'))),
                'currency': order.get('currency', 'USD'),
                'financial_status': order.get('status', ''),  # WooCommerce: pending, processing, completed
                'fulfillment_status': 'fulfilled' if order.get('status') == 'completed' else 'unfulfilled',
                'order_date': datetime.fromisoformat(order['date_created'].replace('Z', '+00:00')),
                'customer': {
                    'platform_customer_id': str(order.get('customer_id', '')),
                    'email': billing.get('email', ''),
                    'first_name': billing.get('first_name', ''),
                    'last_name': billing.get('last_name', ''),
                },
                'items': [
                    {
                        'platform_line_item_id': str(item['id']),
                        'platform_product_id': str(item.get('product_id', '')),
                        'sku': item.get('sku', ''),
                        'product_title': item.get('name', ''),
                        'quantity': item.get('quantity', 0),
                        'price': Decimal(str(item.get('price', '0.00'))),
                        'total_price': Decimal(str(item.get('total', '0.00'))),
                    }
                    for item in order.get('line_items', [])
                ],
            })
        
        return orders
    
    async def get_order_by_id(self, platform_order_id: str) -> Optional[Dict[str, Any]]:
        """Fetch single WooCommerce order."""
        try:
            response = await self.client.get(f"{self.api_base}/orders/{platform_order_id}")
            response.raise_for_status()
            
            order = response.json()
            billing = order.get('billing', {})
            
            return {
                'platform_order_id': str(order['id']),
                'order_number': str(order.get('number', '')),
                'total_price': Decimal(str(order.get('total', '0.00'))),
                'subtotal_price': Decimal(str(sum(Decimal(item['subtotal']) for item in order.get('line_items', [])))),
                'total_tax': Decimal(str(order.get('total_tax', '0.00'))),
                'total_shipping': Decimal(str(order.get('shipping_total', '0.00'))),
                'total_discounts': Decimal(str(order.get('discount_total', '0.00'))),
                'currency': order.get('currency', 'USD'),
                'financial_status': order.get('status', ''),
                'fulfillment_status': 'fulfilled' if order.get('status') == 'completed' else 'unfulfilled',
                'order_date': datetime.fromisoformat(order['date_created'].replace('Z', '+00:00')),
                'customer': {
                    'platform_customer_id': str(order.get('customer_id', '')),
                    'email': billing.get('email', ''),
                    'first_name': billing.get('first_name', ''),
                    'last_name': billing.get('last_name', ''),
                },
                'items': [
                    {
                        'platform_line_item_id': str(item['id']),
                        'platform_product_id': str(item.get('product_id', '')),
                        'sku': item.get('sku', ''),
                        'product_title': item.get('name', ''),
                        'quantity': item.get('quantity', 0),
                        'price': Decimal(str(item.get('price', '0.00'))),
                        'total_price': Decimal(str(item.get('total', '0.00'))),
                    }
                    for item in order.get('line_items', [])
                ],
            }
        except httpx.HTTPStatusError:
            return None
    
    # ========================================================================
    # Customer Data
    # ========================================================================
    
    async def sync_customers(
        self,
        limit: int = 100,
        page: int = 1,
        updated_since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch customers from WooCommerce."""
        params = {"per_page": min(limit, 100), "page": page}
        
        response = await self.client.get(f"{self.api_base}/customers", params=params)
        response.raise_for_status()
        
        customers_data = response.json()
        customers = []
        
        for customer in customers_data:
            customers.append({
                'platform_customer_id': str(customer['id']),
                'email': customer.get('email', ''),
                'first_name': customer.get('first_name', ''),
                'last_name': customer.get('last_name', ''),
                'phone': customer.get('billing', {}).get('phone', ''),
                'total_orders': customer.get('orders_count', 0),
                'total_spent': Decimal(str(customer.get('total_spent', '0.00'))),
                'first_order_date': datetime.fromisoformat(customer['date_created'].replace('Z', '+00:00')) if customer.get('date_created') else None,
                'last_order_date': None,
            })
        
        return customers
    
    # ========================================================================
    # Inventory Tracking
    # ========================================================================
    
    async def get_inventory_level(self, platform_product_id: str) -> int:
        """Get WooCommerce product inventory."""
        product = await self.get_product_by_id(platform_product_id)
        return product.get('inventory_quantity', 0) if product else 0
    
    async def update_inventory(self, platform_product_id: str, quantity: int) -> bool:
        """Update WooCommerce inventory."""
        try:
            response = await self.client.put(
                f"{self.api_base}/products/{platform_product_id}",
                json={"stock_quantity": quantity}
            )
            response.raise_for_status()
            return True
        except Exception:
            return False
    
    # ========================================================================
    # Webhook Management
    # ========================================================================
    
    async def register_webhooks(self, webhook_url: str) -> List[str]:
        """Register WooCommerce webhooks."""
        topics = [
            {"topic": "product.created", "name": "Product Created"},
            {"topic": "product.updated", "name": "Product Updated"},
            {"topic": "product.deleted", "name": "Product Deleted"},
            {"topic": "order.created", "name": "Order Created"},
            {"topic": "order.updated", "name": "Order Updated"},
            {"topic": "customer.created", "name": "Customer Created"},
            {"topic": "customer.updated", "name": "Customer Updated"},
        ]
        
        registered = []
        
        for topic_info in topics:
            try:
                response = await self.client.post(
                    f"{self.api_base}/webhooks",
                    json={
                        "name": topic_info["name"],
                        "topic": topic_info["topic"],
                        "delivery_url": f"{webhook_url}/woocommerce/{topic_info['topic'].replace('.', '_')}",
                    }
                )
                if response.status_code in [200, 201]:
                    registered.append(topic_info["topic"])
            except Exception:
                continue
        
        return registered
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify WooCommerce webhook signature."""
        computed_signature = base64.b64encode(
            hmac.new(
                secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        return hmac.compare_digest(computed_signature, signature)
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    async def get_store_info(self) -> Dict[str, Any]:
        """Get WooCommerce store information."""
        response = await self.client.get(f"{self.api_base}/system_status")
        response.raise_for_status()
        
        settings = response.json().get('settings', {})
        
        return {
            'store_name': settings.get('woocommerce_store_name', ''),
            'store_url': self.site_url,
            'email': settings.get('admin_email', ''),
            'currency': settings.get('currency', 'USD'),
            'timezone': settings.get('timezone_string', ''),
            'plan': 'WooCommerce',  # WooCommerce is a plugin, not SaaS
        }
