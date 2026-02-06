"""
Shopify Connector for SyncPortal™

Implements OAuth2 authentication and REST/GraphQL API integration with Shopify.

Shopify API Documentation:
- REST Admin API: https://shopify.dev/docs/api/admin-rest
- GraphQL Admin API: https://shopify.dev/docs/api/admin-graphql
- Webhooks: https://shopify.dev/docs/api/admin-rest/2024-01/resources/webhook

Required Scopes:
- read_products (product catalog)
- read_orders (order history)
- read_customers (customer data)
- read_inventory (stock levels)
- write_inventory (optional, for circuit breaker auto-updates)
"""
import hmac
import hashlib
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
from . import BaseCMSConnector


class ShopifyConnector(BaseCMSConnector):
    """
    Shopify platform connector using Admin API (REST + GraphQL).
    """
    
    API_VERSION = "2024-01"  # Shopify API version
    
    def __init__(self, store_id: int, credentials: Dict[str, Any]):
        super().__init__(store_id, credentials)
        self.shop_domain = credentials.get('shop_domain')  # e.g., "my-store.myshopify.com"
        self.access_token = credentials.get('access_token')
        self.api_base = f"https://{self.shop_domain}/admin/api/{self.API_VERSION}"
        
        self.client = httpx.AsyncClient(
            headers={
                "X-Shopify-Access-Token": self.access_token,
                "Content-Type": "application/json",
            },
            timeout=30.0
        )
    
    # ========================================================================
    # OAuth & Authentication
    # ========================================================================
    
    def verify_credentials(self) -> bool:
        """Verify Shopify access token by calling shop endpoint."""
        try:
            response = httpx.get(
                f"{self.api_base}/shop.json",
                headers={"X-Shopify-Access-Token": self.access_token}
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def refresh_token(self) -> Optional[str]:
        """Shopify tokens don't expire, no refresh needed."""
        return None
    
    # ========================================================================
    # Product Catalog
    # ========================================================================
    
    async def sync_products(
        self,
        limit: int = 250,
        page: int = 1,
        updated_since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch products from Shopify."""
        params = {
            "limit": min(limit, 250),  # Shopify max is 250
            "page": page,
            "status": "active"  # Only active products
        }
        
        if updated_since:
            params["updated_at_min"] = updated_since.isoformat()
        
        response = await self.client.get(f"{self.api_base}/products.json", params=params)
        response.raise_for_status()
        
        data = response.json()
        products = []
        
        for product in data.get('products', []):
            # Shopify products can have multiple variants, use first variant for pricing
            variant = product.get('variants', [{}])[0]
            
            products.append({
                'platform_product_id': str(product['id']),
                'sku': variant.get('sku', ''),
                'title': product.get('title', ''),
                'description': product.get('body_html', ''),
                'price': Decimal(str(variant.get('price', '0.00'))),
                'inventory_quantity': variant.get('inventory_quantity', 0),
                'in_stock': variant.get('inventory_quantity', 0) > 0,
                'image_url': product.get('image', {}).get('src', ''),
                'product_url': f"https://{self.shop_domain}/products/{product.get('handle', '')}",
                'images': [img['src'] for img in product.get('images', [])],
                'vendor': product.get('vendor', ''),
                'product_type': product.get('product_type', ''),
                'is_active': product.get('status') == 'active',
                'cost_per_item': Decimal(str(variant.get('cost', '0.00'))) if variant.get('cost') else None,
                'compare_at_price': Decimal(str(variant.get('compare_at_price', '0.00'))) if variant.get('compare_at_price') else None,
            })
        
        return products
    
    async def get_product_by_id(self, platform_product_id: str) -> Optional[Dict[str, Any]]:
        """Fetch single Shopify product."""
        try:
            response = await self.client.get(f"{self.api_base}/products/{platform_product_id}.json")
            response.raise_for_status()
            
            product = response.json()['product']
            variant = product.get('variants', [{}])[0]
            
            return {
                'platform_product_id': str(product['id']),
                'sku': variant.get('sku', ''),
                'title': product.get('title', ''),
                'description': product.get('body_html', ''),
                'price': Decimal(str(variant.get('price', '0.00'))),
                'inventory_quantity': variant.get('inventory_quantity', 0),
                'in_stock': variant.get('inventory_quantity', 0) > 0,
                'image_url': product.get('image', {}).get('src', ''),
                'product_url': f"https://{self.shop_domain}/products/{product.get('handle', '')}",
                'images': [img['src'] for img in product.get('images', [])],
                'vendor': product.get('vendor', ''),
                'product_type': product.get('product_type', ''),
                'is_active': product.get('status') == 'active',
            }
        except httpx.HTTPStatusError:
            return None
    
    # ========================================================================
    # Order History
    # ========================================================================
    
    async def sync_orders(
        self,
        limit: int = 250,
        page: int = 1,
        created_since: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch orders from Shopify."""
        params = {
            "limit": min(limit, 250),
            "page": page,
            "status": status or "any"
        }
        
        if created_since:
            params["created_at_min"] = created_since.isoformat()
        
        response = await self.client.get(f"{self.api_base}/orders.json", params=params)
        response.raise_for_status()
        
        data = response.json()
        orders = []
        
        for order in data.get('orders', []):
            customer = order.get('customer', {})
            
            orders.append({
                'platform_order_id': str(order['id']),
                'order_number': str(order.get('order_number', '')),
                'total_price': Decimal(str(order.get('total_price', '0.00'))),
                'subtotal_price': Decimal(str(order.get('subtotal_price', '0.00'))),
                'total_tax': Decimal(str(order.get('total_tax', '0.00'))),
                'total_shipping': Decimal(str(order.get('total_shipping_price_set', {}).get('shop_money', {}).get('amount', '0.00'))),
                'total_discounts': Decimal(str(order.get('total_discounts', '0.00'))),
                'currency': order.get('currency', 'USD'),
                'financial_status': order.get('financial_status', ''),
                'fulfillment_status': order.get('fulfillment_status', 'unfulfilled'),
                'order_date': datetime.fromisoformat(order['created_at'].replace('Z', '+00:00')),
                'customer': {
                    'platform_customer_id': str(customer.get('id', '')) if customer else '',
                    'email': customer.get('email', '') if customer else '',
                    'first_name': customer.get('first_name', '') if customer else '',
                    'last_name': customer.get('last_name', '') if customer else '',
                },
                'items': [
                    {
                        'platform_line_item_id': str(item['id']),
                        'platform_product_id': str(item.get('product_id', '')),
                        'sku': item.get('sku', ''),
                        'product_title': item.get('title', ''),
                        'quantity': item.get('quantity', 0),
                        'price': Decimal(str(item.get('price', '0.00'))),
                        'total_price': Decimal(str(item.get('price', '0.00'))) * item.get('quantity', 0),
                    }
                    for item in order.get('line_items', [])
                ],
            })
        
        return orders
    
    async def get_order_by_id(self, platform_order_id: str) -> Optional[Dict[str, Any]]:
        """Fetch single Shopify order."""
        try:
            response = await self.client.get(f"{self.api_base}/orders/{platform_order_id}.json")
            response.raise_for_status()
            
            order = response.json()['order']
            customer = order.get('customer', {})
            
            return {
                'platform_order_id': str(order['id']),
                'order_number': str(order.get('order_number', '')),
                'total_price': Decimal(str(order.get('total_price', '0.00'))),
                'subtotal_price': Decimal(str(order.get('subtotal_price', '0.00'))),
                'total_tax': Decimal(str(order.get('total_tax', '0.00'))),
                'total_shipping': Decimal(str(order.get('total_shipping_price_set', {}).get('shop_money', {}).get('amount', '0.00'))),
                'total_discounts': Decimal(str(order.get('total_discounts', '0.00'))),
                'currency': order.get('currency', 'USD'),
                'financial_status': order.get('financial_status', ''),
                'fulfillment_status': order.get('fulfillment_status', 'unfulfilled'),
                'order_date': datetime.fromisoformat(order['created_at'].replace('Z', '+00:00')),
                'customer': {
                    'platform_customer_id': str(customer.get('id', '')) if customer else '',
                    'email': customer.get('email', '') if customer else '',
                    'first_name': customer.get('first_name', '') if customer else '',
                    'last_name': customer.get('last_name', '') if customer else '',
                },
                'items': [
                    {
                        'platform_line_item_id': str(item['id']),
                        'platform_product_id': str(item.get('product_id', '')),
                        'sku': item.get('sku', ''),
                        'product_title': item.get('title', ''),
                        'quantity': item.get('quantity', 0),
                        'price': Decimal(str(item.get('price', '0.00'))),
                        'total_price': Decimal(str(item.get('price', '0.00'))) * item.get('quantity', 0),
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
        limit: int = 250,
        page: int = 1,
        updated_since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch customers from Shopify."""
        params = {"limit": min(limit, 250), "page": page}
        
        if updated_since:
            params["updated_at_min"] = updated_since.isoformat()
        
        response = await self.client.get(f"{self.api_base}/customers.json", params=params)
        response.raise_for_status()
        
        data = response.json()
        customers = []
        
        for customer in data.get('customers', []):
            customers.append({
                'platform_customer_id': str(customer['id']),
                'email': customer.get('email', ''),
                'first_name': customer.get('first_name', ''),
                'last_name': customer.get('last_name', ''),
                'phone': customer.get('phone', ''),
                'total_orders': customer.get('orders_count', 0),
                'total_spent': Decimal(str(customer.get('total_spent', '0.00'))),
                'first_order_date': datetime.fromisoformat(customer['created_at'].replace('Z', '+00:00')) if customer.get('created_at') else None,
                'last_order_date': None,  # Shopify doesn't provide this directly
            })
        
        return customers
    
    # ========================================================================
    # Inventory Tracking
    # ========================================================================
    
    async def get_inventory_level(self, platform_product_id: str) -> int:
        """Get Shopify product inventory."""
        product = await self.get_product_by_id(platform_product_id)
        return product.get('inventory_quantity', 0) if product else 0
    
    async def update_inventory(self, platform_product_id: str, quantity: int) -> bool:
        """Update Shopify inventory (requires write_inventory scope)."""
        try:
            # First, get the variant ID
            product_response = await self.client.get(f"{self.api_base}/products/{platform_product_id}.json")
            product_response.raise_for_status()
            variant_id = product_response.json()['product']['variants'][0]['id']
            
            # Get inventory item ID
            variant_response = await self.client.get(f"{self.api_base}/variants/{variant_id}.json")
            variant_response.raise_for_status()
            inventory_item_id = variant_response.json()['variant']['inventory_item_id']
            
            # Get inventory level ID
            levels_response = await self.client.get(f"{self.api_base}/inventory_levels.json?inventory_item_ids={inventory_item_id}")
            levels_response.raise_for_status()
            location_id = levels_response.json()['inventory_levels'][0]['location_id']
            
            # Update inventory
            update_response = await self.client.post(
                f"{self.api_base}/inventory_levels/set.json",
                json={
                    "location_id": location_id,
                    "inventory_item_id": inventory_item_id,
                    "available": quantity
                }
            )
            update_response.raise_for_status()
            return True
        except Exception:
            return False
    
    # ========================================================================
    # Webhook Management
    # ========================================================================
    
    async def register_webhooks(self, webhook_url: str) -> List[str]:
        """Register Shopify webhooks."""
        topics = [
            "products/create",
            "products/update",
            "products/delete",
            "orders/create",
            "orders/updated",
            "orders/paid",
            "orders/fulfilled",
            "inventory_levels/update",
            "customers/create",
            "customers/update",
        ]
        
        registered = []
        
        for topic in topics:
            try:
                response = await self.client.post(
                    f"{self.api_base}/webhooks.json",
                    json={
                        "webhook": {
                            "topic": topic,
                            "address": f"{webhook_url}/shopify/{topic.replace('/', '_')}",
                            "format": "json"
                        }
                    }
                )
                if response.status_code in [200, 201]:
                    registered.append(topic)
            except Exception:
                continue
        
        return registered
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify Shopify webhook HMAC signature."""
        computed_hmac = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(computed_hmac, signature)
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    async def get_store_info(self) -> Dict[str, Any]:
        """Get Shopify store information."""
        response = await self.client.get(f"{self.api_base}/shop.json")
        response.raise_for_status()
        
        shop = response.json()['shop']
        
        return {
            'store_name': shop.get('name', ''),
            'store_url': f"https://{shop.get('domain', '')}",
            'email': shop.get('email', ''),
            'currency': shop.get('currency', 'USD'),
            'timezone': shop.get('timezone', ''),
            'plan': shop.get('plan_name', ''),
        }
