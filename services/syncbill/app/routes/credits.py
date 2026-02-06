"""
Credit Memo Routes

Handles credit issuance for Zero-Risk Policy implementation.

When to issue credits:
1. SyncShield rollback caused revenue loss → Auto-credit
2. KIKI underperformance after invoice sent → Manual credit
3. Client disputes attribution → Review and credit
4. Goodwill gesture → Manual credit
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import Invoice, CreditMemo
from app.services.stripe_service import StripeService
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Stripe service
stripe_service = StripeService(api_key=settings.stripe_secret_key)


# Request/Response models
class CreditRequest(BaseModel):
    """Request to issue credit memo"""
    invoice_id: int
    credit_amount: float = Field(..., gt=0)
    reason_code: str = Field(..., description="rollback, underperformance, dispute, goodwill")
    reason_description: str
    reference_id: Optional[str] = None  # SyncShield rollback ID, ticket ID
    

class CreditResponse(BaseModel):
    """Credit memo response"""
    credit_id: int
    credit_number: str
    credit_amount: float
    reason_code: str
    status: str
    issue_date: datetime
    expiry_date: Optional[datetime]
    message: str


@router.post("/issue", response_model=CreditResponse)
async def issue_credit_memo(
    request: CreditRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Issue credit memo to customer.
    
    Flow:
    1. Validate invoice exists and is paid/sent
    2. Create CreditMemo record
    3. Create Stripe credit note (if Stripe invoice)
    4. Credit will be applied to next invoice
    
    Zero-Risk Policy:
    If KIKI underperforms, client gets automatic credit.
    Example: Charged $5,000 in Jan, but Feb showed negative uplift
    → Issue $5,000 credit for Feb invoice
    """
    logger.info(f"💳 Issuing credit memo for invoice {request.invoice_id}")
    
    # Validate reason code
    valid_reasons = ["rollback", "underperformance", "dispute", "goodwill"]
    if request.reason_code not in valid_reasons:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid reason_code. Must be one of: {valid_reasons}"
        )
    
    # Fetch invoice
    stmt = select(Invoice).where(Invoice.id == request.invoice_id)
    result = await db.execute(stmt)
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Validate credit amount doesn't exceed invoice total
    if request.credit_amount > float(invoice.total_amount):
        raise HTTPException(
            status_code=400,
            detail=f"Credit amount (${request.credit_amount}) exceeds invoice total (${invoice.total_amount})"
        )
    
    # Generate credit number
    credit_number = f"CR-{invoice.invoice_number}"
    
    # Create credit memo
    credit = CreditMemo(
        credit_number=credit_number,
        invoice_id=invoice.id,
        store_id=invoice.store_id,
        credit_amount=Decimal(str(request.credit_amount)),
        currency=invoice.currency,
        reason_code=request.reason_code,
        reason_description=request.reason_description,
        trigger_event=f"api_request_{request.reason_code}",
        reference_id=request.reference_id,
        status="issued",
        issue_date=datetime.utcnow(),
        expiry_date=datetime.utcnow() + timedelta(days=365),  # 1 year expiry
        created_by="api"
    )
    
    db.add(credit)
    await db.commit()
    await db.refresh(credit)
    
    logger.info(f"✅ Credit memo created: {credit_number} for ${request.credit_amount}")
    
    # Create Stripe credit note if invoice has Stripe ID
    if invoice.stripe_invoice_id and settings.stripe_secret_key:
        try:
            stripe_credit_note_id = await stripe_service.create_credit_note(
                stripe_invoice_id=invoice.stripe_invoice_id,
                credit_amount=Decimal(str(request.credit_amount)),
                reason=request.reason_description
            )
            
            # Update credit memo with Stripe reference
            credit.stripe_credit_note_id = stripe_credit_note_id
            await db.commit()
            
            logger.info(f"✅ Stripe credit note created: {stripe_credit_note_id}")
        except Exception as e:
            logger.error(f"❌ Failed to create Stripe credit note: {e}")
            # Continue - credit memo still valid even if Stripe fails
    
    return CreditResponse(
        credit_id=credit.id,
        credit_number=credit.credit_number,
        credit_amount=float(credit.credit_amount),
        reason_code=credit.reason_code,
        status=credit.status,
        issue_date=credit.issue_date,
        expiry_date=credit.expiry_date,
        message=f"Credit of ${request.credit_amount} issued successfully. Will be applied to next invoice."
    )


@router.get("/store/{store_id}")
async def get_store_credits(
    store_id: int,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all credit memos for a store.
    
    Filter by status: draft, issued, applied, expired
    """
    logger.info(f"📋 Fetching credits for store {store_id}")
    
    query = select(CreditMemo).where(CreditMemo.store_id == store_id)
    
    if status:
        query = query.where(CreditMemo.status == status)
    
    query = query.order_by(CreditMemo.issue_date.desc())
    
    result = await db.execute(query)
    credits = result.scalars().all()
    
    credits_list = []
    for credit in credits:
        credits_list.append({
            "credit_id": credit.id,
            "credit_number": credit.credit_number,
            "credit_amount": float(credit.credit_amount),
            "reason_code": credit.reason_code,
            "reason_description": credit.reason_description,
            "status": credit.status,
            "issue_date": credit.issue_date.isoformat(),
            "expiry_date": credit.expiry_date.isoformat() if credit.expiry_date else None,
            "applied_to_invoice_id": credit.applied_to_invoice_id,
            "applied_at": credit.applied_at.isoformat() if credit.applied_at else None
        })
    
    total_available = sum(
        float(c.credit_amount) 
        for c in credits 
        if c.status == "issued" and not c.applied_to_invoice_id
    )
    
    logger.info(f"✅ Found {len(credits)} credits for store {store_id}")
    
    return {
        "store_id": store_id,
        "total_credits": len(credits),
        "total_available_credits": total_available,
        "credits": credits_list
    }


@router.post("/auto-issue-rollback-credit")
async def auto_issue_rollback_credit(
    store_id: int,
    rollback_id: str,
    revenue_loss: float = Field(..., gt=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Automatically issue credit when SyncShield triggers rollback.
    
    Called by SyncShield when:
    - A/B test winner caused revenue drop
    - Ad campaign optimization backfired
    - Pricing change lost sales
    
    Credit = revenue_loss × 0.20 (success fee rate)
    
    Example:
    - Rollback caused $2,000 revenue loss
    - Auto-issue $400 credit (to offset 20% fee client would have paid)
    """
    logger.info(f"🔄 Auto-issuing rollback credit for store {store_id}")
    
    if not settings.auto_issue_credits:
        raise HTTPException(
            status_code=400,
            detail="Auto credit issuance is disabled. Contact support."
        )
    
    # Calculate credit amount (20% of revenue loss)
    credit_amount = revenue_loss * 0.20
    
    # Find most recent paid invoice for this store
    stmt = select(Invoice).where(
        Invoice.store_id == store_id,
        Invoice.payment_status == "paid"
    ).order_by(Invoice.paid_at.desc()).limit(1)
    
    result = await db.execute(stmt)
    recent_invoice = result.scalar_one_or_none()
    
    if not recent_invoice:
        logger.warning(f"⚠️  No paid invoices found for store {store_id}, cannot issue credit")
        raise HTTPException(
            status_code=404,
            detail="No paid invoices found for this store"
        )
    
    # Create credit memo
    credit = CreditMemo(
        credit_number=f"CR-ROLLBACK-{rollback_id[:8]}",
        invoice_id=recent_invoice.id,
        store_id=store_id,
        credit_amount=Decimal(str(credit_amount)),
        currency="USD",
        reason_code="rollback",
        reason_description=f"Zero-Risk Policy: Auto-credit for SyncShield rollback {rollback_id}. Revenue loss: ${revenue_loss:.2f}.",
        trigger_event="syncshield_rollback",
        reference_id=rollback_id,
        status="issued",
        issue_date=datetime.utcnow(),
        expiry_date=datetime.utcnow() + timedelta(days=365),
        created_by="syncshield_auto"
    )
    
    db.add(credit)
    await db.commit()
    await db.refresh(credit)
    
    logger.info(f"✅ Auto-credit issued: ${credit_amount} for rollback {rollback_id}")
    
    return {
        "credit_id": credit.id,
        "credit_number": credit.credit_number,
        "credit_amount": float(credit.credit_amount),
        "rollback_id": rollback_id,
        "revenue_loss": revenue_loss,
        "message": f"Zero-Risk Policy activated: ${credit_amount} credit issued for ${revenue_loss} revenue loss"
    }
