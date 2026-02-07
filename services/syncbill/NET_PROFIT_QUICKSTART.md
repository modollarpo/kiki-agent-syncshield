# SyncBill™ Net Profit Uplift Model - Quick Start

## 🎯 What Changed

**Before**: SyncBill charged 20% of **gross revenue uplift** (ignoring ad costs)  
**After**: SyncBill charges 20% of **Net Profit Uplift** (revenue increase - ad spend increase)

---

## 📊 New Invoice Structure

### Invoice Model (Updated)
```python
class Invoice(Base):
    # Revenue metrics
    baseline_revenue: Decimal
    actual_revenue: Decimal
    incremental_revenue: Decimal
    
    # Ad Spend metrics (NEW)
    baseline_ad_spend: Decimal
    actual_ad_spend: Decimal
    incremental_ad_spend: Decimal
    
    # Net Profit metrics (NEW)
    net_profit_uplift: Decimal  # incremental_revenue - incremental_ad_spend
    baseline_profit: Decimal    # baseline_revenue - baseline_ad_spend
    actual_profit: Decimal      # actual_revenue - actual_ad_spend
    
    # Client value (NEW)
    client_net_gain: Decimal    # net_profit_uplift - subtotal (fee)
    client_roi: Decimal         # client_net_gain / subtotal
    
    # Invoice amounts
    subtotal: Decimal           # 20% of net_profit_uplift (NOT incremental_revenue)
```

---

## 🚀 Quick Start

### 1. Database Migration

Run the migration to add Net Profit fields:

```bash
cd /workspaces/kiki-agent-syncshield/services/syncbill

# Option A: Using Alembic
alembic revision --autogenerate -m "add_net_profit_fields"
alembic upgrade head

# Option B: Manual SQL
psql -U postgres -d syncbill -f migrations/001_add_net_profit_fields.py
```

### 2. Update Invoice Creation

The ledger listener now automatically calculates Net Profit fields:

```python
# In ledger_listener.py (already updated)
async def _generate_invoice_from_settlement(...):
    # Calculate Net Profit
    baseline_profit = baseline_revenue - baseline_ad_spend
    actual_profit = current_revenue - actual_ad_spend
    net_profit_uplift = incremental_revenue - incremental_ad_spend
    
    # Success fee on Net Profit (not gross)
    success_fee = net_profit_uplift * 0.20
    
    # Client metrics
    client_net_gain = net_profit_uplift - success_fee
    client_roi = client_net_gain / success_fee if success_fee > 0 else 0
    
    invoice = Invoice(
        net_profit_uplift=net_profit_uplift,
        client_net_gain=client_net_gain,
        client_roi=client_roi,
        subtotal=success_fee,
        ...
    )
```

### 3. API Endpoints (New)

#### Get Profit Transparency
```bash
GET /api/v1/profit-transparency/store/{store_id}/current
```

**Response**:
```json
{
  "store_id": 123,
  "billing_period": "2026-01",
  "invoice_number": "KIKI-202601-000123",
  "baseline": {
    "revenue": 100000.00,
    "ad_spend": 20000.00,
    "profit": 80000.00
  },
  "current": {
    "revenue": 150000.00,
    "ad_spend": 30000.00,
    "profit": 120000.00
  },
  "uplift": {
    "gross_revenue_increase": 50000.00,
    "ad_spend_increase": 10000.00,
    "net_profit_increase": 40000.00
  },
  "oaas_fee": {
    "success_fee_percentage": 20.0,
    "net_profit_uplift": 40000.00,
    "success_fee_amount": 8000.00,
    "client_net_gain": 32000.00,
    "client_roi": 4.0
  },
  "comparison": {
    "if_billed_on_gross_revenue": 10000.00,
    "actual_bill_on_net_profit": 8000.00,
    "client_savings": 2000.00,
    "fairness_note": "KIKI charges on Net Profit, not gross revenue"
  }
}
```

#### Get Profit Trend
```bash
GET /api/v1/profit-transparency/store/{store_id}/trend?months=12
```

**Response**:
```json
{
  "store_id": 123,
  "baseline_profit": 80000.00,
  "months": [
    {
      "month": "2026-01",
      "revenue": 150000.00,
      "ad_spend": 30000.00,
      "net_profit": 120000.00
    },
    {
      "month": "2026-02",
      "revenue": 160000.00,
      "ad_spend": 32000.00,
      "net_profit": 128000.00
    }
  ]
}
```

#### Get Profit Summary (All-Time)
```bash
GET /api/v1/profit-transparency/store/{store_id}/summary
```

**Response**:
```json
{
  "store_id": 123,
  "total_invoices_paid": 12,
  "total_net_profit_uplift": 480000.00,
  "total_success_fees_paid": 96000.00,
  "total_client_net_gain": 384000.00,
  "overall_roi": 4.0,
  "interpretation": "For every $1 paid to KIKI, you kept $4.00 in profit."
}
```

#### Get Model Explanation
```bash
GET /api/v1/profit-transparency/explanation
```

Returns detailed explanation of Net Profit vs Gross Revenue models.

---

## 📄 PDF Invoice Updates

The PDF invoice now shows:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERFORMANCE BREAKDOWN (Net Profit Model)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Metric          Before KIKI    With KIKI      Uplift
Revenue         $100,000       $150,000       +$50,000
Ad Spend        $20,000        $30,000        +$10,000
Net Profit      $80,000        $120,000       +$40,000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Net Profit Uplift: $40,000
KIKI Success Fee (20%): $8,000
Your Net Gain (80%): $32,000
Your ROI: 4.0x (For every $1 paid to KIKI, you keep $4.00)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INVOICE DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Success Fee (20% of $40,000 Net Profit Uplift)   $8,000.00
Tax (20%)                                         $1,600.00
Total                                             $9,600.00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ ZERO-RISK GUARANTEE (Net Profit Model)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KIKI only charges on Net Profit Uplift (revenue 
increase minus ad spend increase), not gross revenue.

If your net profit goes down, your success fee is 
automatically $0.00.

Why Net Profit vs Gross Revenue?
• You pay ad platforms directly (you own the accounts)
• KIKI manages budget via API-only access
• If ad costs consume the revenue gain, we don't get paid
• This ensures KIKI's success is aligned with your bottom line

Your Protection: You only pay when you truly profit.
```

---

## 🧪 Testing

### Test Invoice Creation
```python
# Test creating an invoice with Net Profit data
from app.models import Invoice
from decimal import Decimal

invoice = Invoice(
    invoice_number="TEST-202602-000001",
    store_id=999,
    platform="shopify",
    customer_name="Test Store",
    customer_email="test@example.com",
    billing_month=2,
    billing_year=2026,
    
    # Revenue
    baseline_revenue=Decimal("100000.00"),
    actual_revenue=Decimal("150000.00"),
    incremental_revenue=Decimal("50000.00"),
    uplift_percentage=Decimal("50.00"),
    
    # Ad Spend (Net Profit Model)
    baseline_ad_spend=Decimal("20000.00"),
    actual_ad_spend=Decimal("30000.00"),
    incremental_ad_spend=Decimal("10000.00"),
    
    # Net Profit
    net_profit_uplift=Decimal("40000.00"),  # 50k - 10k
    baseline_profit=Decimal("80000.00"),     # 100k - 20k
    actual_profit=Decimal("120000.00"),      # 150k - 30k
    
    # Client Value
    subtotal=Decimal("8000.00"),             # 20% of 40k
    client_net_gain=Decimal("32000.00"),     # 40k - 8k
    client_roi=Decimal("4.00"),              # 32k / 8k
    
    total_amount=Decimal("8000.00"),
    amount_due=Decimal("8000.00")
)
```

### Test API Endpoints
```bash
# Start SyncBill service
cd /workspaces/kiki-agent-syncshield/services/syncbill
python -m app.main

# Test profit transparency endpoint
curl http://localhost:8008/api/v1/profit-transparency/store/123/current

# Test trend endpoint
curl http://localhost:8008/api/v1/profit-transparency/store/123/trend?months=12

# Test summary endpoint
curl http://localhost:8008/api/v1/profit-transparency/store/123/summary

# Test explanation endpoint
curl http://localhost:8008/api/v1/profit-transparency/explanation
```

---

## 📋 Integration Checklist

### SyncBill Updates ✅ COMPLETE
- [x] Add Net Profit fields to Invoice model
- [x] Update invoice creation in ledger_listener.py
- [x] Update PDF generation with Net Profit breakdown
- [x] Create profit_transparency.py API routes
- [x] Update InvoiceResponse schema
- [x] Create database migration
- [x] Update Zero-Risk Guarantee text

### Next Steps (Phase 3)
- [ ] Integrate AdSpendFetcher into SyncLedger
- [ ] Update SyncLedger gRPC proto with ad_spend fields
- [ ] Add MarginGuardian to SyncFlow bidding
- [ ] Build React dashboard for Profit Transparency
- [ ] End-to-end testing with real ad account data

---

## 📚 Files Modified

| File | Purpose | Status |
|------|---------|--------|
| `app/models.py` | Added Net Profit fields to Invoice model | ✅ Updated |
| `app/services/ledger_listener.py` | Calculate Net Profit on invoice creation | ✅ Updated |
| `app/services/pdf_service.py` | Show Net Profit in PDF invoices | ✅ Updated |
| `app/routes/invoices.py` | Updated InvoiceResponse schema | ✅ Updated |
| `app/routes/profit_transparency.py` | New API endpoints | ✅ Created |
| `app/routes/__init__.py` | Export profit_transparency router | ✅ Updated |
| `migrations/001_add_net_profit_fields.py` | Database migration | ✅ Created |

---

## 💡 Key Formulas

### Net Profit Uplift
```
NetProfitUplift = (CurrentRevenue - BaselineRevenue) - (CurrentAdSpend - BaselineAdSpend)
```

### Success Fee
```
SuccessFee = NetProfitUplift × 20%
```

### Client Net Gain
```
ClientNetGain = NetProfitUplift - SuccessFee = NetProfitUplift × 80%
```

### Client ROI
```
ClientROI = ClientNetGain ÷ SuccessFee
```

**Example**:
- Baseline: $100k revenue, $20k ad spend = $80k profit
- With KIKI: $150k revenue, $30k ad spend = $120k profit
- Net Profit Uplift: $40k
- Success Fee: $8k (20%)
- Client Net Gain: $32k (80%)
- Client ROI: 4.0x

---

## 🎤 Client Messaging

**"Why does KIKI charge on Net Profit instead of gross revenue?"**

> "Traditional platforms charge 20% of revenue increase, ignoring ad costs. If you gain $50k in revenue but spent $40k more on ads, you only net $10k—but still pay $10k fee.
> 
> KIKI's Net Profit model charges on your actual gain after ad costs. Same example: $50k revenue - $10k ad spend = $40k net profit. You pay $8k (20%), keep $32k (80%), and achieve 4x ROI.
> 
> **We only win when you profit. If ad costs consume the gain, we don't get paid.**"

---

**Built with ❤️ by KIKI Agent™**  
*"From cost center to profit partner—with Net Profit alignment."*
