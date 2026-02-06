"""
Invoice API Routes

Endpoints for invoice management and client dashboard.
"""

import logging
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.database import get_db
from app.models import Invoice, InvoiceLineItem
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic schemas
class InvoiceResponse(BaseModel):
    """Invoice response model"""
    id: int
    invoice_number: str
    store_id: int
    customer_name: str
    billing_period: str
    subtotal: float
    tax_amount: float
    total_amount: float
    amount_due: float
    status: str
    payment_status: str
    issue_date: datetime
    due_date: datetime
    hosted_invoice_url: Optional[str]
    invoice_pdf: Optional[str]
    
    class Config:
        from_attributes = True


class InvoiceSummary(BaseModel):
    """Summary for dashboard"""
    total_invoices: int
    total_amount_billed: float
    total_amount_paid: float
    total_amount_outstanding: float
    invoices_overdue: int


@router.get("/store/{store_id}", response_model=List[InvoiceResponse])
async def get_store_invoices(
    store_id: int,
    status: Optional[str] = Query(None, description="Filter by status"),
    payment_status: Optional[str] = Query(None, description="Filter by payment status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all invoices for a store.
    
    Used by SyncPortal dashboard to show billing history.
    """
    logger.info(f"📋 Fetching invoices for store {store_id}")
    
    # Build query
    query = select(Invoice).where(Invoice.store_id == store_id)
    
    if status:
        query = query.where(Invoice.status == status)
    
    if payment_status:
        query = query.where(Invoice.payment_status == payment_status)
    
    query = query.order_by(Invoice.issue_date.desc())
    
    result = await db.execute(query)
    invoices = result.scalars().all()
    
    logger.info(f"✅ Found {len(invoices)} invoices for store {store_id}")
    
    return [
        InvoiceResponse(
            id=inv.id,
            invoice_number=inv.invoice_number,
            store_id=inv.store_id,
            customer_name=inv.customer_name,
            billing_period=f"{inv.billing_year}-{inv.billing_month:02d}",
            subtotal=float(inv.subtotal),
            tax_amount=float(inv.tax_amount),
            total_amount=float(inv.total_amount),
            amount_due=float(inv.amount_due),
            status=inv.status,
            payment_status=inv.payment_status,
            issue_date=inv.issue_date,
            due_date=inv.due_date,
            hosted_invoice_url=inv.hosted_invoice_url,
            invoice_pdf=inv.invoice_pdf
        )
        for inv in invoices
    ]


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice_details(
    invoice_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed invoice information"""
    logger.info(f"📄 Fetching invoice {invoice_id}")
    
    stmt = select(Invoice).where(Invoice.id == invoice_id)
    result = await db.execute(stmt)
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return InvoiceResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        store_id=invoice.store_id,
        customer_name=invoice.customer_name,
        billing_period=f"{invoice.billing_year}-{invoice.billing_month:02d}",
        subtotal=float(invoice.subtotal),
        tax_amount=float(invoice.tax_amount),
        total_amount=float(invoice.total_amount),
        amount_due=float(invoice.amount_due),
        status=invoice.status,
        payment_status=invoice.payment_status,
        issue_date=invoice.issue_date,
        due_date=invoice.due_date,
        hosted_invoice_url=invoice.hosted_invoice_url,
        invoice_pdf=invoice.invoice_pdf
    )


@router.get("/summary/{store_id}", response_model=InvoiceSummary)
async def get_invoice_summary(
    store_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get invoice summary for store dashboard.
    
    Shows:
    - Total invoices
    - Total billed vs paid
    - Outstanding balance
    - Overdue invoices
    """
    logger.info(f"📊 Calculating invoice summary for store {store_id}")
    
    # Get all invoices
    stmt = select(Invoice).where(Invoice.store_id == store_id)
    result = await db.execute(stmt)
    invoices = result.scalars().all()
    
    if not invoices:
        return InvoiceSummary(
            total_invoices=0,
            total_amount_billed=0.0,
            total_amount_paid=0.0,
            total_amount_outstanding=0.0,
            invoices_overdue=0
        )
    
    # Calculate totals
    total_billed = sum(float(inv.total_amount) for inv in invoices)
    total_paid = sum(float(inv.amount_paid) for inv in invoices)
    total_outstanding = sum(float(inv.amount_due) for inv in invoices if inv.payment_status != "paid")
    overdue_count = sum(1 for inv in invoices if inv.is_overdue)
    
    return InvoiceSummary(
        total_invoices=len(invoices),
        total_amount_billed=total_billed,
        total_amount_paid=total_paid,
        total_amount_outstanding=total_outstanding,
        invoices_overdue=overdue_count
    )
