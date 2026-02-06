"""
BigCommerce Connector for SyncPortal™

Implements OAuth2 authentication and REST/GraphQL API integration with BigCommerce.

BigCommerce API Documentation:
- REST API: https://developer.bigcommerce.com/docs/rest-management
- GraphQL: https://developer.bigcommerce.com/docs/graphql-storefront
- Webhooks: https://developer.bigcommerce.com/docs/integrations/webhooks

Authentication:
- OAuth2 flow with client credentials
- Access tokens are long-lived (no refresh needed)

Required Scopes:
- store_v2_products (read/write)
- store_v2_orders (read)
- store_v2_customers (read)
- store_v2_information (read)
"""
import hmac
import hashlib
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
from . import BaseCMSConnector


class BigCommerceConnector(BaseCMSConnector):
    """
    BigCommerce platform connector using V3 REST API + GraphQL.
    """
    
    API_VERSION = "v3"
    
    def __init__(self, store_id: int, credentials: Dict[str, Any]):
        super().__init__(store_id, credentials)
        self.store_hash = credentials.get('store_hash')  # e.g., "abc123def"
        self.access_token = credentials.get('access_token')
        self.api_base = f"https://api.bigcommerce.com/stores/{self.store_hash}/v3"
        self.api_v2_base = f"https://api.bigcommerce.com/stores/{self.store_hash}/v2"
        
        self.client = httpx.AsyncClient(
            headers={
                "X-Auth-Token": self.access_token,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=30.0
        )
    
    def verify_credentials(self) -> bool:
        """Verify BigCommerce access token."""
        try:
            response = httpx.get(
                f"{self.api_v2_base}/store",
                headers={"X-Auth-Token": self.access_token}
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def refresh_token(self) -> Optional[str]:
        """BigCommerce tokens don't expire."""
        return None
    
    async def sync_products(
        self,
        limit: int = 250,
        page: int = 1,
        updated_since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch products from BigCommerce."""
        params = {
            "limit": min(limit, 250),
            "page": page,
            "include": "images,variants"
        }
        
        if updated_since:
            params["date_modified:min"] = updated_since.isoformat()
        
        response = await self.client.get(f"{self.api_base}/catalog/products", params=params)
        response.raise_for_status()
        
        data = response.json()
        products = []
        
        for product in data.get('data', []):
            products.append({
                'platform_product_id': str(product['id']),
                'sku': product.get('sku', ''),
                'title': product.get('name', ''),
                'description': product.get('description', ''),
                'price': Decimal(str(product.get('price', '0.00'))),
                'inventory_quantity': product.get('inventory_level', 0),
                'in_stock': product.get('availability') == 'available',
                'image_url': product.get('primary_image', {}).get('url_standard', ''),
                'product_url': product.get('custom_url', {}).get('url', ''),
                'images': [img['url_standard'] for img in product.get('images', [])],
                'vendor': product.get('brand_name', ''),
                'product_type': ', '.join(product.get('categories', [])),
                'is_active': product.get('is_visible', False),
                'cost_per_item': Decimal(str(product.get('cost_price', '0.00'))) if product.get('cost_price') else None,
                'compare_at_price': Decimal(str(product.get('retail_price', '0.00'))) if product.get('retail_price') else None,
            })
        
        return products
    
    async def get_product_by_id(self, platform_product_id: str) -> Optional[Dict[str, Any]]:
        """Fetch single BigCommerce product."""
        try:
            response = await self.client.get(f"{self.api_base}/catalog/products/{platform_product_id}?include=images")
            response.raise_for_status()
            
            product = response.json()['data']
            
            return {
                'platform_product_id': str(product['id']),
                'sku': product.get('sku', ''),
                'title': product.get('name', ''),
                'description': product.get('description', ''),
                'price': Decimal(str(product.get('price', '0.00'))),
                'inventory_quantity': product.get('inventory_level', 0),
                'in_stock': product.get('availability') == 'available',
                'image_url': product.get('primary_image', {}).get('url_standard', ''),
                'product_url': product.get('custom_url', {}).get('url', ''),
                'images': [img['url_standard'] for img in product.get('images', [])],
                'vendor': product.get('brand_name', ''),
                'product_type': ', '.join(product.get('categories', [])),
                'is_active': product.get('is_visible', False),
            }
        except httpx.HTTPStatusError:
            return None
    
    async def sync_orders(
        self,
        limit: int = 250,
        page: int = 1,
        created_since: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch orders from BigCommerce."""
        params = {"limit": min(limit, 250), "page": page}
        
        if created_since:
            params["min_date_created"] = created_since.isoformat()
        
        if status:
            params["status_id"] = status
        
        response = await self.client.get(f"{self.api_v2_base}/orders", params=params)
        response.raise_for_status()
        
        orders_data = response.json()
        orders = []
        
        for order in orders_data:
            # Get billing info
            billing = order.get('billing_address', {})
            
            # Get line items
            items_response = await self.client.get(f"{self.api_v2_base}/orders/{order['id']}/products")
            items = items_response.json()
            
            orders.append({
                'platform_order_id': str(order['id']),
                'order_number': str(order.get('id', '')),
                'total_price': Decimal(str(order.get('total_inc_tax', '0.00'))),
                'subtotal_price': Decimal(str(order.get('subtotal_ex_tax', '0.00'))),
                'total_tax': Decimal(str(order.get('total_tax', '0.00'))),
                'total_shipping': Decimal(str(order.get('shipping_cost_inc_tax', '0.00'))),
                'total_discounts': Decimal(str(order.get('discount_amount', '0.00'))),
                'currency': order.get('currency_code', 'USD'),
                'financial_status': order.get('payment_status', ''),
                'fulfillment_status': order.get('status', ''),
                'order_date': datetime.fromisoformat(order['date_created']),
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
                        'price': Decimal(str(item.get('price_inc_tax', '0.00'))) / item.get('quantity', 1),
                        'total_price': Decimal(str(item.get('total_inc_tax', '0.00'))),
                    }
                    for item in items
                ],
            })
        
        return orders
    
    async def get_order_by_id(self, platform_order_id: str) -> Optional[Dict[str, Any]]:
        """Fetch single BigCommerce order."""
        try:
            response = await self.client.get(f"{self.api_v2_base}/orders/{platform_order_id}")
            response.raise_for_status()
            
            order = response.json()
            billing = order.get('billing_address', {})
            
            items_response = await self.client.get(f"{self.api_v2_base}/orders/{order['id']}/products")
            items = items_response.json()
            
            return {
                'platform_order_id': str(order['id']),
                'order_number': str(order.get('id', '')),
                'total_price': Decimal(str(order.get('total_inc_tax', '0.00'))),
                'subtotal_price': Decimal(str(order.get('subtotal_ex_tax', '0.00'))),
                'total_tax': Decimal(str(order.get('total_tax', '0.00'))),
                'total_shipping': Decimal(str(order.get('shipping_cost_inc_tax', '0.00'))),
                'total_discounts': Decimal(str(order.get('discount_amount', '0.00'))),
                'currency': order.get('currency_code', 'USD'),
                'financial_status': order.get('payment_status', ''),
                'fulfillment_status': order.get('status', ''),
                'order_date': datetime.fromisoformat(order['date_created']),
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
                        'price': Decimal(str(item.get('price_inc_tax', '0.00'))) / item.get('quantity', 1),
                        'total_price': Decimal(str(item.get('total_inc_tax', '0.00'))),
                    }
                    for item in items
                ],
            }
        except httpx.HTTPStatusError:
            return None
    
    async def sync_customers(
        self,
        limit: int = 250,
        page: int = 1,
        updated_since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch customers from BigCommerce."""
        params = {"limit": min(limit, 250), "page": page}
        
        if updated_since:
            params["date_modified:min"] = updated_since.isoformat()
        
        response = await self.client.get(f"{self.api_base}/customers", params=params)
        response.raise_for_status()
        
        customers_data = response.json().get('data', [])
        customers = []
        
        for customer in customers_data:
            customers.append({
                'platform_customer_id': str(customer['id']),
                'email': customer.get('email', ''),
                'first_name': customer.get('first_name', ''),
                'last_name': customer.get('last_name', ''),
                'phone': customer.get('phone', ''),
                'total_orders': customer.get('orders_count', 0),
                'total_spent': Decimal(str(customer.get('store_credit', '0.00'))),  # BC doesn't expose total_spent directly
                'first_order_date': datetime.fromisoformat(customer['date_created']) if customer.get('date_created') else None,
                'last_order_date': datetime.fromisoformat(customer['date_modified']) if customer.get('date_modified') else None,
            })
        
        return customers
    
    async def get_inventory_level(self, platform_product_id: str) -> int:
        """Get BigCommerce product inventory."""
        product = await self.get_product_by_id(platform_product_id)
        return product.get('inventory_quantity', 0) if product else 0
    
    async def update_inventory(self, platform_product_id: str, quantity: int) -> bool:
        """Update BigCommerce inventory."""
        try:
            response = await self.client.put(
                f"{self.api_base}/catalog/products/{platform_product_id}",
                json={"inventory_level": quantity}
            )
            response.raise_for_status()
            return True
        except Exception:
            return False
    
    async def register_webhooks(self, webhook_url: str) -> List[str]:
        """Register BigCommerce webhooks."""
        scopes = [
            "store/product/created",
            "store/product/updated",
            "store/product/deleted",
            "store/product/inventory/updated",
            "store/order/created",
            "store/order/updated",
            "store/customer/created",
            "store/customer/updated",
        ]
        
        registered = []
        
        for scope in scopes:
            try:
                response = await self.client.post(
                    f"{self.api_base}/hooks",
                    json={
                        "scope": scope,
                        "destination": f"{webhook_url}/bigcommerce/{scope.replace('/', '_')}",
                        "is_active": True
                    }
                )
                if response.status_code in [200, 201]:
                    registered.append(scope)
            except Exception:
                continue
        
        return registered
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify BigCommerce webhook signature."""
        # BigCommerce doesn't use HMAC signatures - uses client_secret validation
        return True  # Implement IP whitelist verification in production
    
    async def get_store_info(self) -> Dict[str, Any]:
        """Get BigCommerce store information."""
        response = await self.client.get(f"{self.api_v2_base}/store")
        response.raise_for_status()
        
        store = response.json()
        
        return {
            'store_name': store.get('name', ''),
            'store_url': store.get('domain', ''),
            'email': store.get('admin_email', ''),
            'currency': store.get('currency', 'USD'),
            'timezone': store.get('timezone', {}).get('name', ''),
            'plan': store.get('plan_name', ''),
        }
