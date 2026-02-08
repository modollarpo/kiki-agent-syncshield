# KIKI Agent™ - Net Profit Uplift Implementation

**Status:** ✅ **COMPLETE** - Ready for Antler Pitch

**Business Model Transformation:**
- **Before:** KIKI charged 20% of *gross revenue increase*
- **After:** KIKI charges 20% of *net profit increase* (revenue - ad spend)
- **Why:** Aligns incentives - if ads cost more than they generate, KIKI fee = $0

---

## Implementation Summary

### 1. ✅ SyncLedger™ (Go) - Net Profit Calculator

**File:** `services/syncledger/internal/calculator.go`

**New Method:** `CalculateNetProfitAttribution()`

```go
func (u *UpliftCalculator) CalculateNetProfitAttribution(
    currentRevenue, baselineRevenue float64,
    currentAdSpend, baselineAdSpend float64,
    confidence float64,
    signalScores map[string]float64,
) *AttributionDecision {
    grossUplift := currentRevenue - baselineRevenue
    adSpendIncrease := currentAdSpend - baselineAdSpend
    netProfitUplift := grossUplift - adSpendIncrease
    
    // Zero-Risk: If net profit <= 0, fee = $0
    if netProfitUplift <= 0 {
        return &AttributionDecision{
            Attributed: false,
            SuccessFeeAmount: 0.00,
        }
    }
    
    successFee := netProfitUplift * 0.20  // 20% of NET profit
    clientNetGain := netProfitUplift * 0.80
    clientROI := clientNetGain / successFee
    
    return decision
}
```

**Database Models Updated:**
- `LedgerEntry` now tracks:
  - `AdSpendForOrder` - Ad spend attributed to this order
  - `BaselineAdSpend` - Historical average ad spend
  - `IncrementalAdSpend` - Difference (current - baseline)
  - `NetProfitUplift` - Revenue increase minus ad spend increase

**Status:** ✅ Compiled (30MB binary), ready to deploy

---

### 2. ✅ AdSpendFetcher Service (Python)

**File:** `services/syncledger/app/services/ad_spend_fetcher.py` (450 lines)

**Purpose:** Fetch real-time ad spend from Meta and Google Ads APIs

**Classes:**
- `AdSpendFetcher`: Integrates with Meta/Google APIs to get campaign spend
- `MarginGuardian`: Validates CPA < LTV before placing bids (prevents overspending)

**Example Usage:**
```python
fetcher = AdSpendFetcher()
meta_spend = fetcher.fetch_meta_spend(
    campaign_id="campaign_123_meta",
    date_range=("2026-01-01", "2026-01-31")
)
# Returns: {"total_spend": 10500.00, "impressions": 125000, "clicks": 3500}
```

**MarginGuardian Logic:**
```python
if cpa > ltv:
    return {"approved": False, "reason": "CPA $120 exceeds LTV $100"}
else:
    return {"approved": True, "max_bid": ltv * 0.70}  # 70% safety margin
```

**Status:** ✅ Installed packages (stripe, facebook-business, google-ads)

---

### 3. ✅ SyncBill™ (Python) - Invoice Updates

**Files Updated:**
- `app/models.py` - Added 10 new Net Profit fields to `Invoice` model
- `app/services/pdf_service.py` - PDF invoices now show Net Profit breakdown
- `app/routes/profit_transparency.py` - 3 new API endpoints (280 lines)

**Invoice Model Changes:**
```python
class Invoice(Base):
    # NEW: Net Profit fields
    baseline_ad_spend = Column(Numeric(12, 2), default=0.0)
    actual_ad_spend = Column(Numeric(12, 2), default=0.0)
    incremental_ad_spend = Column(Numeric(12, 2), default=0.0)
    net_profit_uplift = Column(Numeric(12, 2), default=0.0)
    client_net_gain = Column(Numeric(12, 2), default=0.0)
    client_roi = Column(Numeric(5, 2), default=0.0)
```

**PDF Invoice Output:**
```
Metric          Before KIKI    With KIKI      Uplift
Revenue         $100,000       $150,000       +$50,000
Ad Spend        $20,000        $30,000        +$10,000
Net Profit      $80,000        $120,000       +$40,000

KIKI Success Fee (20% of $40k Net): $8,000
Your Net Gain (80%): $32,000
Your ROI: 4.0x
```

**Status:** ✅ 22 tests passing

---

### 4. ✅ Profit Transparency API (Python FastAPI)

**File:** `services/syncbill/app/routes/profit_transparency.py`

**Endpoints:**

#### GET `/profit-transparency/store/{store_id}/current`
Returns current period Net Profit breakdown

**Response:**
```json
{
  "storeId": 123,
  "period": {"start": "2026-01-01", "end": "2026-01-31", "label": "Jan 2026"},
  "baseline": {"revenue": 100000, "adSpend": 20000, "netProfit": 80000},
  "current": {"revenue": 150000, "adSpend": 30000, "netProfit": 120000},
  "uplift": {"revenue": 50000, "adSpend": 10000, "netProfit": 40000, "percentIncrease": 50.0},
  "fees": {"kikiSuccessFee": 8000, "clientNetGain": 32000, "clientROI": 4.0}
}
```

#### GET `/profit-transparency/store/{store_id}/trend?months=12`
Returns 12-month Net Profit trend

#### GET `/profit-transparency/store/{store_id}/summary`
Returns all-time cumulative Net Profit stats

**Status:** ✅ API operational, ready for frontend integration

---

### 5. ✅ MarginGuardian for SyncFlow™ (Go)

**File:** `services/syncflow/internal/margin_guardian.go` (240 lines)

**Purpose:** Prevent KIKI from losing money on ad bids

**How It Works:**
1. Before placing bid, predict customer LTV (call SyncValue)
2. Calculate max safe CPA = LTV × 70% (safety margin)
3. If bid > max CPA → reject or cap bid
4. Tracks `bids_capped_total` and `bids_rejected_total` metrics

**Example:**
```go
guardian := NewMarginGuardian()
decision, _ := guardian.EvaluateBid(ctx, "user123", 120.00)

// If LTV = $150:
// Max CPA = $150 * 0.70 = $105
// Bid $120 > $105 → Capped to $105
decision.Approved = true
decision.ApprovedBid = 105.00
decision.RiskLevel = "capped"
decision.Reason = "Bid $120 exceeds max CPA $105, capped"
```

**Integration:** Updated `ExecuteBidHandler` in `handlers_bid.go` to call MarginGuardian before executing bids

**Status:** ✅ SyncFlow compiled (31MB binary), MarginGuardian active

---

### 6. ✅ ProfitTransparency React Component

**Files Created:**
- `packages/ui/src/ProfitTransparency.tsx` - React component (240 lines)
- `packages/ui/src/ProfitTransparency.css` - Styling (280 lines)
- `packages/ui/src/stories/ProfitTransparency.stories.tsx` - Storybook stories

**Features:**
- 📊 Visual Net Profit breakdown (Before vs. With KIKI)
- 💰 Key metrics: Net Profit Uplift, KIKI Fee (20%), Client Gain (80%)
- 📈 Client ROI calculator (auto-updates)
- 🧮 Step-by-step profit calculation explanation
- 🔄 Auto-refresh every 60s (configurable)
- 📱 Responsive design (mobile + desktop)

**Usage:**
```tsx
import { ProfitTransparency } from '@kiki/ui';

<ProfitTransparency
  storeId={123}
  apiEndpoint="http://syncbill:8000/profit-transparency"
  showDetailedBreakdown={true}
  refreshInterval={60000}
/>
```

**Storybook:**
- View at `http://localhost:6006/?path=/story/kiki-profittransparency`
- 5 stories: Default, SmallBusiness, MinimalView, Loading, ErrorState

**Status:** ✅ Component ready, exported in `index.ts`

---

## Architecture Changes

### Service Communication Flow

```
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│   SyncPortal    │        │   SyncValue     │        │   SyncFlow      │
│  (Attribution)  │───────>│ (LTV Predict)   │<───────│ (Real-time Bid) │
└────────┬────────┘        └─────────────────┘        └────────┬────────┘
         │                                                      │
         │ 1. Order attributed?                                │ 2. Fetch LTV
         │    Confidence: 0.85                                 │    MarginGuardian
         │                                                      │    CPA < LTV?
         v                                                      v
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│  SyncLedger™    │<───────│  AdSpendFetcher │───────>│  Meta/Google    │
│ (Net Profit Calc)│        │  (Ad Spend API) │        │   Ads APIs      │
└────────┬────────┘        └─────────────────┘        └─────────────────┘
         │
         │ 3. Calculate Net Profit:
         │    Revenue Increase - Ad Spend Increase
         │    Fee = 20% of Net Profit
         │
         v
┌─────────────────┐        ┌─────────────────┐
│   SyncBill™     │───────>│   Client UI     │
│  (Invoice Gen)  │        │ (Profit Display)│
└─────────────────┘        └─────────────────┘
```

### Data Flow Example

**Scenario:** Client gets a $100 order attributed to KIKI

1. **SyncPortal** → Attribution engine: Confidence 85% → Call SyncLedger
2. **SyncLedger** → Fetch baseline: $70 avg order, $15 avg ad spend
3. **AdSpendFetcher** → Meta API: This order cost $20 in ads
4. **Calculator**:
   - Revenue increase: $100 - $70 = $30
   - Ad spend increase: $20 - $15 = $5
   - **Net Profit: $30 - $5 = $25**
   - KIKI fee: $25 × 20% = **$5.00**
   - Client gain: $25 × 80% = **$20.00**
   - Client ROI: $20 / $5 = **4.0x**
5. **SyncBill** → Creates invoice with Net Profit breakdown
6. **Client Dashboard** → Displays ProfitTransparency component

---

## Database Migrations

### SyncLedger (PostgreSQL)

```sql
-- Add Net Profit fields to ledger_entries
ALTER TABLE ledger_entries ADD COLUMN ad_spend_for_order DECIMAL(12, 2) DEFAULT 0.0;
ALTER TABLE ledger_entries ADD COLUMN baseline_ad_spend DECIMAL(12, 2) DEFAULT 0.0;
ALTER TABLE ledger_entries ADD COLUMN incremental_ad_spend DECIMAL(12, 2) DEFAULT 0.0;
ALTER TABLE ledger_entries ADD COLUMN net_profit_uplift DECIMAL(12, 2) DEFAULT 0.0;

-- Add Net Profit fields to baseline_snapshots
ALTER TABLE baseline_snapshots ADD COLUMN total_ad_spend DECIMAL(15, 2) DEFAULT 0.0;
ALTER TABLE baseline_snapshots ADD COLUMN avg_ad_spend_per_order DECIMAL(10, 2) DEFAULT 0.0;
```

### SyncBill (PostgreSQL)

```sql
-- Add Net Profit fields to invoices
ALTER TABLE invoices ADD COLUMN baseline_ad_spend DECIMAL(12, 2) DEFAULT 0.0;
ALTER TABLE invoices ADD COLUMN actual_ad_spend DECIMAL(12, 2) DEFAULT 0.0;
ALTER TABLE invoices ADD COLUMN incremental_ad_spend DECIMAL(12, 2) DEFAULT 0.0;
ALTER TABLE invoices ADD COLUMN net_profit_uplift DECIMAL(12, 2) DEFAULT 0.0;
ALTER TABLE invoices ADD COLUMN client_net_gain DECIMAL(12, 2) DEFAULT 0.0;
ALTER TABLE invoices ADD COLUMN client_roi DECIMAL(5, 2) DEFAULT 0.0;
```

**Status:** ✅ Migration scripts ready (`/services/syncbill/app/database_migrations.sql`)

---

## Testing

### SyncBill Tests
```bash
cd /workspaces/kiki-agent-syncshield/services/syncbill
python -m pytest tests/ -v
# Result: 22 passed, 35 warnings (deprecation warnings only)
```

### SyncLedger Build
```bash
cd /workspaces/kiki-agent-syncshield/services/syncledger
go build -o syncledger
# Result: SUCCESS (30MB binary)
```

### SyncFlow Build
```bash
cd /workspaces/kiki-agent-syncshield/services/syncflow
go build -o syncflow
# Result: SUCCESS (31MB binary)
```

---

## Deployment Checklist

### 1. Environment Variables

**SyncLedger:**
```bash
DATABASE_URL=postgres://user:pass@postgres:5432/kiki_ledger
KIKI_INTERNAL_API_KEY=your-secret-key
```

**SyncBill:**
```bash
DATABASE_URL=postgres://user:pass@postgres:5432/kiki_billing
SYNCLEDGER_GRPC_URL=syncledger:50053
STRIPE_API_KEY=sk_live_...
```

**AdSpendFetcher:**
```bash
META_ACCESS_TOKEN=your-meta-token
META_AD_ACCOUNT_ID=act_123456789
GOOGLE_ADS_DEVELOPER_TOKEN=your-google-token
GOOGLE_ADS_CLIENT_ID=123-456-789.apps.googleusercontent.com
```

### 2. Docker Compose

```yaml
services:
  syncledger:
    build: ./services/syncledger
    ports:
      - "50053:50053"  # gRPC
      - "8090:8090"    # HTTP/metrics
    environment:
      DATABASE_URL: ${DATABASE_URL}
  
  syncbill:
    build: ./services/syncbill
    ports:
      - "8000:8000"
    environment:
      SYNCLEDGER_GRPC_URL: syncledger:50053
  
  syncflow:
    build: ./services/syncflow
    ports:
      - "8080:8080"
    environment:
      SYNCVALUE_URL: http://syncvalue:8080
```

### 3. Kubernetes (Optional)

```bash
kubectl apply -f deploy/k8s/syncledger-deployment.yaml
kubectl apply -f deploy/k8s/syncbill-deployment.yaml
kubectl apply -f deploy/k8s/syncflow-deployment.yaml
```

### 4. Health Checks

```bash
# SyncLedger
curl http://localhost:8090/healthz
# {"status":"healthy","service":"syncledger"}

# SyncBill
curl http://localhost:8000/healthz
# {"status":"healthy"}

# SyncFlow
curl http://localhost:8080/healthz
# {"status":"ok"}
```

---

## Metrics & Monitoring

### Prometheus Metrics

**SyncLedger:**
- `syncledger_revenue_attributed_total{store_id, platform}`
- `syncledger_success_fee_calculated_total{store_id}`
- `syncledger_attribution_latency_ms`

**SyncFlow:**
- `syncflow_bid_requests_total{endpoint, method}`
- `syncflow_bids_capped_total` ← **NEW** (MarginGuardian)
- `syncflow_bids_rejected_total` ← **NEW** (MarginGuardian)
- `syncflow_bid_latency_seconds`

**SyncBill:**
- `syncbill_invoices_generated_total`
- `syncbill_payment_failures_total`
- `syncbill_net_profit_total` ← **NEW**

### Grafana Dashboards

**Net Profit Uplift Dashboard:**
- Total Net Profit Uplift (all clients)
- KIKI Success Fees (20%)
- Client Net Gains (80%)
- Average Client ROI
- MarginGuardian: Bids Capped vs. Rejected

**JSON Config:** `/deploy/grafana/net-profit-dashboard.json`

---

## Business Impact

### Before Net Profit Model:
- **Revenue:** $50k increase
- **Ad Spend:** $10k increase (paid by client)
- **KIKI Fee:** $50k × 20% = **$10k**
- **Client keeps:** $50k - $10k ads - $10k KIKI = **$30k**
- **Client ROI:** $30k / $10k = **3.0x**

### After Net Profit Model:
- **Revenue:** $50k increase
- **Ad Spend:** $10k increase (paid by client)
- **Net Profit:** $50k - $10k = $40k
- **KIKI Fee:** $40k × 20% = **$8k** ← Lower!
- **Client keeps:** $40k - $8k = **$32k** ← Higher!
- **Client ROI:** $32k / $8k = **4.0x** ← Better!

### Zero-Risk Example:
- **Revenue:** $20k increase
- **Ad Spend:** $25k increase *(overspent!)*
- **Net Profit:** $20k - $25k = **-$5k**
- **KIKI Fee:** $0 (net profit ≤ 0)
- **Client Loss:** -$5k (but KIKI shares the loss by not charging)

---

## Next Steps

### Phase 1 (COMPLETE ✅)
- [x] Update calculator to Net Profit model
- [x] Create AdSpendFetcher service
- [x] Update SyncBill invoice generation
- [x] Create Profit Transparency API
- [x] Add MarginGuardian to SyncFlow
- [x] Create ProfitTransparency React component

### Phase 2 (Optional Enhancements)
- [ ] Add SyncValue LTV prediction integration
- [ ] Create 12-month trend chart in UI
- [ ] Add Slack notifications for Net Profit milestones
- [ ] Build admin dashboard for KIKI team
- [ ] Add A/B testing for MarginGuardian safety margins

### Phase 3 (Scaling)
- [ ] Multi-currency support (EUR, GBP, etc.)
- [ ] White-label profit transparency for clients
- [ ] API rate limiting and caching
- [ ] Real-time WebSocket updates

---

## Documentation

- **Architecture:** `/docs/ARCHITECTURE.md`
- **API Reference:** `/docs/API_REFERENCE.md`
- **Agent Spec:** `/docs/AGENT_SPEC.md`
- **Business Plan:** `/docs/BUSINESS_PLAN.md`
- **Deployment:** `/deploy/DEPLOYMENT_GUIDE.md`
- **Copilot Instructions:** `/.github/copilot-instructions.md`

---

## Support

**Contact:**
- GitHub: [modollarpo/kiki-agent-syncshield](https://github.com/modollarpo/kiki-agent-syncshield)
- Slack: #kiki-dev
- Email: dev@kiki-agent.com

**Antler Pitch Deck:** `/docs/KIKI_EXECUTIVE_SUMMARY.md`

---

## License

Proprietary - KIKI Agent™ © 2026

**Confidential:** This is an internal implementation document. Do not share outside KIKI team.
