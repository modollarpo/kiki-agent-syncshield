"""
Stripe Webhook Handler

Processes Stripe webhook events:
- invoice.paid: Update invoice status, create payment record
- invoice.payment_failed: Notify customer, retry payment
- customer.subscription.deleted: Handle cancellation
- credit_note.created: Track credit memo
"""

import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import get_db
from app.models import Invoice, Payment
from app.services.stripe_service import StripeService
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Stripe service (singleton)
stripe_service = StripeService(api_key=settings.stripe_secret_key)


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    
    Stripe sends webhooks for:
    - invoice.paid (payment successful)
    - invoice.payment_failed (payment failed)
    - invoice.finalized (invoice sent to customer)
    - customer.subscription.deleted (subscription cancelled)
    
    Security: Verifies webhook signature using STRIPE_WEBHOOK_SECRET
    """
    logger.info("🔔 Received Stripe webhook")
    
    # Get raw payload and signature
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        logger.error("❌ Missing Stripe signature header")
        raise HTTPException(status_code=400, detail="Missing signature header")
    
    # Verify webhook signature
    try:
        event = stripe_service.construct_webhook_event(payload, sig_header)
    except ValueError as e:
        logger.error(f"❌ Invalid webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception as e:
        logger.error(f"❌ Webhook verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Process event by type
    event_type = event["type"]
    event_data = event["data"]["object"]
    
    logger.info(f"📨 Processing webhook: {event_type}")
    
    if event_type == "invoice.paid":
        await handle_invoice_paid(event_data, db)
    
    elif event_type == "invoice.payment_failed":
        await handle_invoice_payment_failed(event_data, db)
    
    elif event_type == "invoice.finalized":
        await handle_invoice_finalized(event_data, db)
    
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_deleted(event_data, db)
    
    else:
        logger.info(f"ℹ️  Unhandled webhook event: {event_type}")
    
    return {"status": "success", "event_type": event_type}


async def handle_invoice_paid(event_data: dict, db: AsyncSession):
    """
    Process invoice.paid webhook.
    
    Flow:
    1. Extract KIKI invoice ID from Stripe metadata
    2. Create Payment record
    3. Update Invoice status to "paid"
    4. TODO: Notify SyncPortal to update client dashboard
    5. TODO: Notify SyncShield to update Trust Score
    """
    stripe_invoice_id = event_data["id"]
    amount_paid = event_data["amount_paid"] / 100  # Convert from cents
    payment_intent_id = event_data.get("payment_intent")
    payment_method = event_data.get("default_payment_method", "card")
    
    # Get KIKI invoice ID from metadata
    metadata = event_data.get("metadata", {})
    kiki_invoice_id = metadata.get("kiki_invoice_id")
    
    if not kiki_invoice_id:
        logger.error(f"❌ Missing kiki_invoice_id in Stripe invoice {stripe_invoice_id}")
        return
    
    logger.info(f"💰 Invoice paid: Stripe {stripe_invoice_id} → KIKI {kiki_invoice_id} → ${amount_paid}")
    
    # Fetch invoice from database
    stmt = select(Invoice).where(Invoice.id == int(kiki_invoice_id))
    result = await db.execute(stmt)
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        logger.error(f"❌ Invoice {kiki_invoice_id} not found in database")
        return
    
    # Create payment record
    payment = Payment(
        payment_reference=f"STRIPE-{payment_intent_id[:12]}" if payment_intent_id else f"STRIPE-{stripe_invoice_id[:12]}",
        invoice_id=invoice.id,
        store_id=invoice.store_id,
        amount=amount_paid,
        currency=invoice.currency,
        payment_method=payment_method,
        payment_date=datetime.utcnow(),
        status="completed",
        stripe_payment_intent_id=payment_intent_id,
        stripe_charge_id=event_data.get("charge"),
        processed_by="stripe_webhook"
    )
    
    db.add(payment)
    
    # Update invoice status
    invoice.payment_status = "paid"
    invoice.amount_paid = amount_paid
    invoice.amount_due = 0.0
    invoice.paid_at = datetime.utcnow()
    invoice.status = "paid"
    
    await db.commit()
    
    logger.info(f"✅ Payment processed: ${amount_paid} for invoice {invoice.invoice_number}")
    
    # TODO: Notify SyncPortal via gRPC or webhook
    # await notify_syncportal(invoice.store_id, "invoice_paid", invoice.id)


async def handle_invoice_payment_failed(event_data: dict, db: AsyncSession):
    """
    Process invoice.payment_failed webhook.
    
    Actions:
    1. Update invoice status to "payment_failed"
    2. TODO: Send notification to customer support
    3. TODO: Retry payment with different method
    """
    stripe_invoice_id = event_data["id"]
    metadata = event_data.get("metadata", {})
    kiki_invoice_id = metadata.get("kiki_invoice_id")
    
    logger.warning(f"⚠️  Payment failed for Stripe invoice {stripe_invoice_id}")
    
    if not kiki_invoice_id:
        return
    
    # Update invoice status
    stmt = select(Invoice).where(Invoice.id == int(kiki_invoice_id))
    result = await db.execute(stmt)
    invoice = result.scalar_one_or_none()
    
    if invoice:
        invoice.status = "payment_failed"
        await db.commit()
        logger.info(f"✅ Marked invoice {invoice.invoice_number} as payment_failed")
        
        # TODO: Send notification to customer
        # TODO: Notify support team


async def handle_invoice_finalized(event_data: dict, db: AsyncSession):
    """
    Process invoice.finalized webhook.
    
    Invoice has been sent to customer.
    """
    stripe_invoice_id = event_data["id"]
    metadata = event_data.get("metadata", {})
    kiki_invoice_id = metadata.get("kiki_invoice_id")
    
    logger.info(f"📤 Invoice finalized: {stripe_invoice_id}")
    
    if not kiki_invoice_id:
        return
    
    # Update invoice status
    stmt = select(Invoice).where(Invoice.id == int(kiki_invoice_id))
    result = await db.execute(stmt)
    invoice = result.scalar_one_or_none()
    
    if invoice and invoice.status == "draft":
        invoice.status = "sent"
        invoice.sent_at = datetime.utcnow()
        await db.commit()
        logger.info(f"✅ Invoice {invoice.invoice_number} marked as sent")


async def handle_subscription_deleted(event_data: dict, db: AsyncSession):
    """
    Process customer.subscription.deleted webhook.
    
    Customer has cancelled their OaaS subscription.
    """
    subscription_id = event_data["id"]
    customer_id = event_data["customer"]
    
    logger.warning(f"🚫 Subscription deleted: {subscription_id} for customer {customer_id}")
    
    # TODO: Mark customer as inactive in database
    # TODO: Send offboarding notification
    # TODO: Notify SyncPortal to update status
