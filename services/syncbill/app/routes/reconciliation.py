"""
Payment Reconciliation Routes

Handles manual payment reconciliation for bank transfers,
checks, and other non-Stripe payment methods.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import Invoice, Payment

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response models
class ManualPaymentRequest(BaseModel):
    """Request to record manual payment"""
    invoice_id: int
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., description="bank_transfer, check, wire, ach")
    payment_date: datetime
    bank_reference: Optional[str] = None
    notes: Optional[str] = None


class ReconciliationResponse(BaseModel):
    """Payment reconciliation response"""
    payment_id: int
    invoice_id: int
    invoice_number: str
    amount: float
    payment_method: str
    status: str
    message: str


@router.post("/manual-payment", response_model=ReconciliationResponse)
async def record_manual_payment(
    request: ManualPaymentRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Record manual payment (bank transfer, check, etc.)
    
    Use case:
    - Enterprise clients pay via wire transfer
    - AP department sends check
    - ACH payment received outside Stripe
    
    Process:
    1. Validate invoice exists and is unpaid
    2. Create Payment record
    3. Update Invoice payment status
    4. If fully paid, mark invoice as "paid"
    """
    logger.info(f"💵 Recording manual payment for invoice {request.invoice_id}")
    
    # Fetch invoice
    stmt = select(Invoice).where(Invoice.id == request.invoice_id)
    result = await db.execute(stmt)
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Invoice already paid")
    
    # Create payment record
    payment = Payment(
        payment_reference=f"{request.payment_method.upper()}-{invoice.invoice_number}",
        invoice_id=invoice.id,
        store_id=invoice.store_id,
        amount=Decimal(str(request.amount)),
        currency=invoice.currency,
        payment_method=request.payment_method,
        payment_date=request.payment_date,
        status="completed",
        bank_reference=request.bank_reference,
        notes=request.notes,
        processed_by="manual_reconciliation"
    )
    
    db.add(payment)
    
    # Update invoice
    invoice.amount_paid = float(invoice.amount_paid) + request.amount
    invoice.amount_due = float(invoice.total_amount) - invoice.amount_paid
    
    # Check if fully paid
    if invoice.amount_due <= 0:
        invoice.payment_status = "paid"
        invoice.status = "paid"
        invoice.paid_at = request.payment_date
        message = f"Invoice fully paid (${request.amount})"
        logger.info(f"✅ Invoice {invoice.invoice_number} fully paid")
    elif invoice.amount_paid > 0:
        invoice.payment_status = "partial"
        message = f"Partial payment recorded (${request.amount}). Outstanding: ${invoice.amount_due}"
        logger.info(f"⏳ Partial payment for invoice {invoice.invoice_number}")
    else:
        message = f"Payment recorded (${request.amount})"
    
    await db.commit()
    await db.refresh(payment)
    
    return ReconciliationResponse(
        payment_id=payment.id,
        invoice_id=invoice.id,
        invoice_number=invoice.invoice_number,
        amount=float(payment.amount),
        payment_method=payment.payment_method,
        status=invoice.payment_status,
        message=message
    )


@router.get("/unreconciled")
async def get_unreconciled_invoices(
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of unpaid/partially paid invoices.
    
    For finance team to track outstanding receivables.
    """
    logger.info("📋 Fetching unreconciled invoices")
    
    stmt = select(Invoice).where(
        Invoice.payment_status.in_(["unpaid", "partial"])
    ).order_by(Invoice.due_date.asc())
    
    result = await db.execute(stmt)
    invoices = result.scalars().all()
    
    unreconciled = []
    for inv in invoices:
        unreconciled.append({
            "invoice_id": inv.id,
            "invoice_number": inv.invoice_number,
            "store_id": inv.store_id,
            "customer_name": inv.customer_name,
            "total_amount": float(inv.total_amount),
            "amount_paid": float(inv.amount_paid),
            "amount_due": float(inv.amount_due),
            "due_date": inv.due_date.isoformat(),
            "days_overdue": (datetime.utcnow() - inv.due_date).days if inv.is_overdue else 0,
            "status": inv.status
        })
    
    logger.info(f"✅ Found {len(unreconciled)} unreconciled invoices")
    
    return {
        "count": len(unreconciled),
        "total_outstanding": sum(i["amount_due"] for i in unreconciled),
        "invoices": unreconciled
    }
