"""
Stripe Integration Service

Handles all Stripe API interactions:
- Customer creation
- Invoice generation
- Payment processing
- Webhook handling
- Subscription management (for recurring OaaS fees)

Documentation: https://stripe.com/docs/api
"""

import logging
from decimal import Decimal
from typing import List, Dict, Optional
from datetime import datetime

import stripe
from stripe.error import StripeError

from app.config import settings
from app.models import Invoice, Payment, CreditMemo

logger = logging.getLogger(__name__)


class StripeService:
    """Service for Stripe API operations"""
    
    def __init__(self, api_key: str):
        """Initialize Stripe with secret key"""
        stripe.api_key = api_key
        self.api_key = api_key
        logger.info("✅ Stripe service initialized")
    
    async def create_or_get_customer(
        self,
        store_id: int,
        email: str,
        name: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Create Stripe customer or retrieve existing.
        
        Args:
            store_id: KIKI store ID
            email: Customer email
            name: Store name
            metadata: Additional metadata
        
        Returns:
            Stripe customer ID (cus_xxxxx)
        """
        try:
            # Search for existing customer by email
            customers = stripe.Customer.list(email=email, limit=1)
            
            if customers.data:
                customer = customers.data[0]
                logger.info(f"📇 Found existing Stripe customer: {customer.id}")
                return customer.id
            
            # Create new customer
            customer_metadata = metadata or {}
            customer_metadata.update({
                "kiki_store_id": str(store_id),
                "managed_by": "kiki_agent"
            })
            
            customer = stripe.Customer.create(
                email=email,
                name=name,
                description=f"KIKI Agent™ OaaS Client - Store #{store_id}",
                metadata=customer_metadata
            )
            
            logger.info(f"✨ Created new Stripe customer: {customer.id} for {name}")
            return customer.id
            
        except StripeError as e:
            logger.error(f"❌ Stripe customer creation failed: {e}", exc_info=True)
            raise
    
    async def create_invoice_from_settlement(
        self,
        invoice_record: Invoice
    ) -> Dict:
        """
        Create Stripe invoice from SyncBill invoice record.
        
        Args:
            invoice_record: Database Invoice object
        
        Returns:
            {
                "stripe_invoice_id": "in_xxxxx",
                "hosted_invoice_url": "https://invoice.stripe.com/...",
                "invoice_pdf": "https://pay.stripe.com/invoice/xxxxx/pdf"
            }
        """
        try:
            # Ensure customer exists
            customer_id = await self.create_or_get_customer(
                store_id=invoice_record.store_id,
                email=invoice_record.customer_email,
                name=invoice_record.customer_name
            )
            
            # Create invoice
            stripe_invoice = stripe.Invoice.create(
                customer=customer_id,
                collection_method='send_invoice',  # Email to customer
                days_until_due=settings.invoice_due_days,  # Net 30
                currency=invoice_record.currency.lower(),
                description=f"KIKI Agent™ OaaS Success Fee - {invoice_record.billing_month}/{invoice_record.billing_year}",
                metadata={
                    "kiki_invoice_id": str(invoice_record.id),
                    "kiki_invoice_number": invoice_record.invoice_number,
                    "store_id": str(invoice_record.store_id),
                    "billing_period": f"{invoice_record.billing_year}-{invoice_record.billing_month:02d}",
                    "incremental_revenue": str(invoice_record.incremental_revenue),
                    "uplift_percentage": str(invoice_record.uplift_percentage)
                },
                custom_fields=[
                    {
                        "name": "Billing Period",
                        "value": f"{invoice_record.billing_year}-{invoice_record.billing_month:02d}"
                    },
                    {
                        "name": "Incremental Revenue",
                        "value": f"${invoice_record.incremental_revenue:,.2f}"
                    },
                    {
                        "name": "Uplift",
                        "value": f"{invoice_record.uplift_percentage}%"
                    }
                ]
            )
            
            # Add line items
            # Main success fee
            stripe.InvoiceItem.create(
                customer=customer_id,
                invoice=stripe_invoice.id,
                amount=int(invoice_record.subtotal * 100),  # Convert to cents
                currency=invoice_record.currency.lower(),
                description=f"Success Fee (20% of ${invoice_record.incremental_revenue:,.2f} incremental revenue)",
                metadata={
                    "item_type": "success_fee",
                    "incremental_revenue": str(invoice_record.incremental_revenue)
                }
            )
            
            # Add tax if applicable
            if invoice_record.tax_amount > 0:
                stripe.InvoiceItem.create(
                    customer=customer_id,
                    invoice=stripe_invoice.id,
                    amount=int(invoice_record.tax_amount * 100),
                    currency=invoice_record.currency.lower(),
                    description=f"{invoice_record.tax_rate * 100}% Tax",
                    metadata={"item_type": "tax"}
                )
            
            # Apply credits if any
            if invoice_record.has_credits_applied and invoice_record.credits_applied > 0:
                stripe.InvoiceItem.create(
                    customer=customer_id,
                    invoice=stripe_invoice.id,
                    amount=-int(invoice_record.credits_applied * 100),  # Negative for credit
                    currency=invoice_record.currency.lower(),
                    description="Credit applied from previous period",
                    metadata={"item_type": "credit"}
                )
            
            # Finalize and send invoice
            finalized_invoice = stripe.Invoice.finalize_invoice(stripe_invoice.id)
            
            # Send invoice email
            if settings.send_invoice_emails:
                stripe.Invoice.send_invoice(finalized_invoice.id)
                logger.info(f"📧 Invoice sent to {invoice_record.customer_email}")
            
            logger.info(f"✅ Created Stripe invoice: {finalized_invoice.id} for ${invoice_record.total_amount}")
            
            return {
                "stripe_invoice_id": finalized_invoice.id,
                "stripe_customer_id": customer_id,
                "hosted_invoice_url": finalized_invoice.hosted_invoice_url,
                "invoice_pdf": finalized_invoice.invoice_pdf,
                "status": finalized_invoice.status
            }
            
        except StripeError as e:
            logger.error(f"❌ Stripe invoice creation failed: {e}", exc_info=True)
            raise
    
    async def process_payment_webhook(
        self,
        stripe_invoice_id: str,
        payment_intent_id: str,
        amount_paid: float,
        payment_method: str
    ) -> Payment:
        """
        Process Stripe webhook: invoice.paid
        
        Creates Payment record and updates Invoice status.
        """
        try:
            # Retrieve invoice details from Stripe
            stripe_invoice = stripe.Invoice.retrieve(stripe_invoice_id)
            
            # Extract KIKI invoice ID from metadata
            kiki_invoice_id = stripe_invoice.metadata.get("kiki_invoice_id")
            store_id = int(stripe_invoice.metadata.get("store_id"))
            
            # Create payment record
            payment = Payment(
                payment_reference=f"STRIPE-{payment_intent_id[:12]}",
                invoice_id=int(kiki_invoice_id),
                store_id=store_id,
                amount=Decimal(amount_paid),
                currency=stripe_invoice.currency.upper(),
                payment_method=payment_method,
                payment_date=datetime.utcnow(),
                status="completed",
                stripe_payment_intent_id=payment_intent_id,
                stripe_charge_id=stripe_invoice.charge,
                processed_by="stripe_webhook"
            )
            
            logger.info(f"💰 Payment received: ${amount_paid} for invoice {kiki_invoice_id}")
            return payment
            
        except StripeError as e:
            logger.error(f"❌ Payment webhook processing failed: {e}", exc_info=True)
            raise
    
    async def create_credit_note(
        self,
        stripe_invoice_id: str,
        credit_amount: Decimal,
        reason: str
    ) -> str:
        """
        Create Stripe credit note for invoice.
        
        Used for Zero-Risk Policy: Issue credit when KIKI underperforms.
        
        Returns:
            Credit note ID (cn_xxxxx)
        """
        try:
            # Create credit note
            credit_note = stripe.CreditNote.create(
                invoice=stripe_invoice_id,
                lines=[{
                    "type": "custom_line_item",
                    "description": reason,
                    "quantity": 1,
                    "unit_amount": int(credit_amount * 100),  # Convert to cents
                }],
                reason="product_unsatisfactory",  # Stripe's closest reason
                metadata={
                    "kiki_reason": reason,
                    "zero_risk_policy": "true"
                }
            )
            
            logger.info(f"✅ Credit note created: {credit_note.id} for ${credit_amount}")
            return credit_note.id
            
        except StripeError as e:
            logger.error(f"❌ Credit note creation failed: {e}", exc_info=True)
            raise
    
    async def retrieve_payment_method(
        self,
        stripe_customer_id: str
    ) -> Optional[Dict]:
        """Get customer's default payment method"""
        try:
            customer = stripe.Customer.retrieve(stripe_customer_id)
            
            if customer.invoice_settings.default_payment_method:
                pm_id = customer.invoice_settings.default_payment_method
                payment_method = stripe.PaymentMethod.retrieve(pm_id)
                
                return {
                    "id": payment_method.id,
                    "type": payment_method.type,
                    "card_brand": payment_method.card.brand if payment_method.card else None,
                    "card_last4": payment_method.card.last4 if payment_method.card else None,
                }
            
            return None
            
        except StripeError as e:
            logger.error(f"❌ Payment method retrieval failed: {e}", exc_info=True)
            return None
    
    def construct_webhook_event(self, payload: bytes, sig_header: str):
        """
        Verify and construct Stripe webhook event.
        
        Args:
            payload: Raw request body
            sig_header: Stripe-Signature header
        
        Returns:
            Verified event object
        """
        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=settings.stripe_webhook_secret
            )
            logger.info(f"✅ Webhook verified: {event['type']}")
            return event
            
        except ValueError as e:
            logger.error(f"❌ Invalid webhook payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"❌ Invalid webhook signature: {e}")
            raise
