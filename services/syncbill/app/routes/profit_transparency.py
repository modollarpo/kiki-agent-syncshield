"""
Profit Transparency API Routes

Provides Net Profit Uplift transparency dashboards for clients.
Shows how KIKI's success fee is calculated using Net Profit model.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from pydantic import BaseModel

from app.database import get_db
from app.models import Invoice

logger = logging.getLogger(__name__)

router = APIRouter()


# Response Models
class ProfitMetrics(BaseModel):
    """Profit metrics for a specific period"""
    revenue: float
    ad_spend: float
    profit: float


class UpliftBreakdown(BaseModel):
    """Breakdown of uplift components"""
    gross_revenue_increase: float
    ad_spend_increase: float
    net_profit_increase: float


class OaaSFeeBreakdown(BaseModel):
    """KIKI's OaaS fee breakdown"""
    success_fee_percentage: float  # Always 20%
    net_profit_uplift: float
    success_fee_amount: float
    client_net_gain: float
    client_roi: float


class ProfitTransparencyResponse(BaseModel):
    """Complete profit transparency dashboard data"""
    store_id: int
    billing_period: str
    invoice_number: str
    
    # Before vs After
    baseline: ProfitMetrics
    current: ProfitMetrics
    
    # Uplift breakdown
    uplift: UpliftBreakdown
    
    # OaaS fee
    oaas_fee: OaaSFeeBreakdown
    
    # Comparison (what if we charged on gross?)
    comparison: Optional[dict] = None


class MonthlyTrendPoint(BaseModel):
    """Data point for monthly profit trend"""
    month: str  # YYYY-MM
    revenue: float
    ad_spend: float
    net_profit: float


class ProfitTrendResponse(BaseModel):
    """12-month profit trend"""
    store_id: int
    months: list[MonthlyTrendPoint]
    baseline_profit: float  # Average pre-KIKI profit


@router.get("/store/{store_id}/current", response_model=ProfitTransparencyResponse)
async def get_current_profit_transparency(
    store_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get profit transparency data for the most recent invoice.
    
    Used by client dashboard to show:
    - Before KIKI vs With KIKI comparison
    - Net Profit Uplift calculation
    - Success fee breakdown
    - Client's net gain and ROI
    """
    logger.info(f"📊 Fetching profit transparency for store {store_id}")
    
    # Get most recent invoice
    query = (
        select(Invoice)
        .where(Invoice.store_id == store_id)
        .order_by(Invoice.issue_date.desc())
        .limit(1)
    )
    
    result = await db.execute(query)
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=f"No invoices found for store {store_id}"
        )
    
    # Calculate comparison (what if charged on gross?)
    gross_fee = float(invoice.incremental_revenue) * 0.20
    net_fee = float(invoice.subtotal)
    client_savings = gross_fee - net_fee
    
    return ProfitTransparencyResponse(
        store_id=store_id,
        billing_period=f"{invoice.billing_year}-{invoice.billing_month:02d}",
        invoice_number=invoice.invoice_number,
        
        baseline=ProfitMetrics(
            revenue=float(invoice.baseline_revenue),
            ad_spend=float(invoice.baseline_ad_spend),
            profit=float(invoice.baseline_profit)
        ),
        
        current=ProfitMetrics(
            revenue=float(invoice.actual_revenue),
            ad_spend=float(invoice.actual_ad_spend),
            profit=float(invoice.actual_profit)
        ),
        
        uplift=UpliftBreakdown(
            gross_revenue_increase=float(invoice.incremental_revenue),
            ad_spend_increase=float(invoice.incremental_ad_spend),
            net_profit_increase=float(invoice.net_profit_uplift)
        ),
        
        oaas_fee=OaaSFeeBreakdown(
            success_fee_percentage=20.0,
            net_profit_uplift=float(invoice.net_profit_uplift),
            success_fee_amount=float(invoice.subtotal),
            client_net_gain=float(invoice.client_net_gain),
            client_roi=float(invoice.client_roi)
        ),
        
        comparison={
            "if_billed_on_gross_revenue": gross_fee,
            "actual_bill_on_net_profit": net_fee,
            "client_savings": client_savings,
            "fairness_note": "KIKI charges on Net Profit (revenue - ad spend), not gross revenue. Ad costs are factored in."
        }
    )


@router.get("/store/{store_id}/trend", response_model=ProfitTrendResponse)
async def get_profit_trend(
    store_id: int,
    months: int = Query(12, ge=1, le=24, description="Number of months to include"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get profit trend over time (up to 24 months).
    
    Shows monthly evolution of:
    - Revenue
    - Ad Spend
    - Net Profit (revenue - ad spend)
    
    Used for trend charts in client dashboard.
    """
    logger.info(f"📈 Fetching {months}-month profit trend for store {store_id}")
    
    # Get invoices for the last N months
    query = (
        select(Invoice)
        .where(Invoice.store_id == store_id)
        .order_by(Invoice.billing_year.desc(), Invoice.billing_month.desc())
        .limit(months)
    )
    
    result = await db.execute(query)
    invoices = result.scalars().all()
    
    if not invoices:
        raise HTTPException(
            status_code=404,
            detail=f"No invoice data found for store {store_id}"
        )
    
    # Calculate baseline (use first invoice's baseline)
    baseline_profit = float(invoices[-1].baseline_profit) if invoices else 0.0
    
    # Build trend data
    trend_points = []
    for inv in reversed(invoices):  # Chronological order
        trend_points.append(
            MonthlyTrendPoint(
                month=f"{inv.billing_year}-{inv.billing_month:02d}",
                revenue=float(inv.actual_revenue),
                ad_spend=float(inv.actual_ad_spend),
                net_profit=float(inv.actual_profit)
            )
        )
    
    return ProfitTrendResponse(
        store_id=store_id,
        months=trend_points,
        baseline_profit=baseline_profit
    )


@router.get("/store/{store_id}/summary")
async def get_profit_summary(
    store_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get aggregate profit summary (all-time).
    
    Returns:
    - Total Net Profit Uplift generated
    - Total Success Fees paid to KIKI
    - Total Client Net Gain
    - Overall ROI
    """
    logger.info(f"💰 Fetching profit summary for store {store_id}")
    
    # Aggregate all invoices
    query = (
        select(
            func.sum(Invoice.net_profit_uplift).label('total_net_uplift'),
            func.sum(Invoice.subtotal).label('total_fees'),
            func.sum(Invoice.client_net_gain).label('total_client_gain'),
            func.count(Invoice.id).label('invoice_count')
        )
        .where(
            and_(
                Invoice.store_id == store_id,
                Invoice.payment_status == 'paid'
            )
        )
    )
    
    result = await db.execute(query)
    row = result.one()
    
    total_net_uplift = float(row.total_net_uplift or 0)
    total_fees = float(row.total_fees or 0)
    total_client_gain = float(row.total_client_gain or 0)
    invoice_count = row.invoice_count or 0
    
    # Calculate overall ROI
    overall_roi = 0.0
    if total_fees > 0:
        overall_roi = total_client_gain / total_fees
    
    return {
        "store_id": store_id,
        "total_invoices_paid": invoice_count,
        "total_net_profit_uplift": total_net_uplift,
        "total_success_fees_paid": total_fees,
        "total_client_net_gain": total_client_gain,
        "overall_roi": overall_roi,
        "interpretation": f"For every $1 paid to KIKI, you kept ${overall_roi:.2f} in profit."
    }


@router.get("/explanation")
async def get_net_profit_model_explanation():
    """
    Get explanation of Net Profit vs Gross Revenue billing models.
    
    Educational endpoint for clients to understand pricing.
    """
    return {
        "title": "Why KIKI Charges on Net Profit (Not Gross Revenue)",
        "problem": {
            "gross_model": "Traditional OaaS charges 20% of revenue increase, ignoring ad costs",
            "example_unfairness": {
                "baseline": {"revenue": 100000, "ad_spend": 20000, "profit": 80000},
                "with_platform": {"revenue": 150000, "ad_spend": 50000, "profit": 100000},
                "gross_fee": 10000,
                "client_net_gain": 10000,
                "problem": "Client pays $30k more in ads but only gains $10k profit, then pays $10k fee = $0 net gain!"
            }
        },
        "solution": {
            "net_profit_model": "KIKI charges 20% of Net Profit Uplift (revenue increase - ad spend increase)",
            "example_fairness": {
                "baseline": {"revenue": 100000, "ad_spend": 20000, "profit": 80000},
                "with_kiki": {"revenue": 150000, "ad_spend": 30000, "profit": 120000},
                "net_profit_uplift": 40000,
                "kiki_fee": 8000,
                "client_net_gain": 32000,
                "client_roi": 4.0,
                "benefit": "Client gains $40k net profit, pays $8k (20%), keeps $32k (4x ROI)"
            }
        },
        "why_net_model": [
            "Client pays ad platforms directly (they own accounts)",
            "KIKI manages budget via API-only access",
            "If ad costs consume the revenue gain, KIKI doesn't get paid",
            "Aligns KIKI's success with client's bottom line",
            "Zero-Risk Policy: If net profit goes down, fee = $0"
        ],
        "client_control": [
            "Client maintains own Meta/Google ad accounts",
            "Full data ownership and security",
            "KIKI has read/write API access only",
            "Client can revoke access anytime"
        ]
    }
