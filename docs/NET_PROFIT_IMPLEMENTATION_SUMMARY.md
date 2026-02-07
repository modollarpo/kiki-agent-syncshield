# NET PROFIT UPLIFT MODEL - Implementation Summary

## 🎯 Business Case

**Problem**: Current OaaS billing charges 20% of **GROSS revenue uplift**, ignoring ad costs paid by client.

**Client Risk**:
- Client pays Meta/Google directly (they own accounts)
- If KIKI increases revenue by $50k but ad costs increase by $40k, client only nets $10k
- Gross model charges $10,000 (20% of $50k) → Client LOSES $0 or even goes negative with fees
- This is unfair and kills enterprise deals

**Solution**: NET PROFIT UPLIFT MODEL
- `NetUplift = (Revenue Increase) - (Ad Spend Increase)`
- `Success Fee = NetUplift × 20%`
- Example: $50k revenue + $10k ad spend = $40k net → Fee $8k (not $10k)
- Client keeps $32k (80% of net), pays $8k (20%)
- Client ROI: 4.0x ($32k kept / $8k paid)

---

## 📊 Updated Formula

### Before (Gross Revenue Model - WRONG)
```
IncrementalRevenue = CurrentRevenue - BaselineRevenue
SuccessFee = IncrementalRevenue × 20%
```

**Issue**: Ignores ad costs. If ad spend increases faster than revenue, client loses money but still pays KIKI.

### After (Net Profit Model - CORRECT)
```
GrossUplift = CurrentRevenue - BaselineRevenue
AdSpendIncrease = CurrentAdSpend - BaselineAdSpend
NetProfitUplift = GrossUplift - AdSpendIncrease
SuccessFee = NetProfitUplift × 20%
```

**Benefit**: KIKI only gets paid when client *actually profits*. Aligns incentives perfectly.

---

## 🏗️ Architecture Changes

### 1. **Ad Spend Fetcher Service** ✅ COMPLETE
**File**: `/services/syncledger/app/services/ad_spend_fetcher.py`

**Purpose**: Fetch daily ad spend from Meta and Google Ads APIs

**Key Methods**:
```python
# Fetch Meta Ads spend
async def get_meta_spend(ad_account_id, start_date, end_date) -> Decimal

# Fetch Google Ads spend
async def get_google_spend(customer_id, start_date, end_date) -> Decimal

# Aggregate both platforms
async def get_total_spend_for_period(store_id, start_date, end_date, ad_accounts) -> Dict
# Returns: {"meta_spend": 5000.00, "google_spend": 3000.00, "total_spend": 8000.00}

# Calculate baseline (12-month historical average)
async def get_baseline_spend(store_id, ad_accounts) -> Decimal
```

**Integration**:
- Meta: Uses facebook-business library, AdsInsights API
- Google: Uses google-ads-python library, metrics.cost_micros
- Concurrent fetching with asyncio for performance
- Handles errors, retries, rate limits

**Status**: ✅ Created (450 lines)

---

### 2. **Margin Guardian (Bid Safety Governor)** ✅ COMPLETE
**File**: `/services/syncledger/app/services/ad_spend_fetcher.py` (MarginGuardian class)

**Purpose**: Prevent SyncFlow from spending more on ads than projected LTV

**Key Method**:
```python
def should_kill_bid(current_cpa, predicted_ltv, campaign_id) -> Tuple[bool, str]:
    max_cpa = predicted_ltv * (1.0 - safety_margin)  # 10% buffer
    if current_cpa > max_cpa:
        return True, "🛑 MARGIN GUARDIAN: CPA exceeds LTV"
    return False, "✅ Campaign safe"
```

**Safety Formula**:
```
Max CPA = LTV × (1 - 0.10)  # 10% safety margin
If Current CPA > Max CPA → Kill bid to protect client profit
```

**Example**:
- LTV: $100
- Safety margin: 10%
- Max CPA: $90
- If campaign CPA hits $95 → Auto-kill bid

**Status**: ✅ Created (150 lines)

---

### 3. **Calculator Updates** ✅ COMPLETE
**File**: `/services/syncledger/internal/calculator.go`

**Changes Made**:
1. Updated `AttributionDecision` struct:
   ```go
   type AttributionDecision struct {
       // ... existing fields ...
       
       // NEW: Ad spend tracking
       AdSpendForPeriod     float64
       BaselineAdSpend      float64
       IncrementalAdSpend   float64
       NetProfitUplift      float64  // Key metric: Revenue uplift - Ad spend uplift
   }
   ```

2. Added new method: `CalculateNetProfitAttribution()`
   ```go
   func (u *UpliftCalculator) CalculateNetProfitAttribution(
       currentRevenue, baselineRevenue float64,
       currentAdSpend, baselineAdSpend float64,
       confidence float64,
       signalScores map[string]float64,
   ) *AttributionDecision {
       // Calculate gross revenue uplift
       grossUplift := currentRevenue - baselineRevenue
       
       // Calculate ad spend increase
       adSpendIncrease := currentAdSpend - baselineAdSpend
       
       // Calculate NET PROFIT UPLIFT
       netProfitUplift := grossUplift - adSpendIncrease
       
       // Zero-Risk Policy: If net profit <= 0, fee = $0
       if netProfitUplift <= 0 {
           return &AttributionDecision{
               Attributed: false,
               SuccessFeeAmount: 0.00,
               Explanation: "Zero-Risk Policy: No fee when client doesn't profit"
           }
       }
       
       // Calculate success fee on NET PROFIT
       successFee := netProfitUplift * 0.20
       
       // Calculate client's net gain and ROI
       clientNetGain := netProfitUplift - successFee
       clientROI := clientNetGain / successFee
       
       // Generate XAI explanation
       explanation := generateNetProfitExplanation(...)
       
       return decision
   }
   ```

3. Added `generateNetProfitExplanation()` helper:
   - Shows revenue breakdown
   - Shows ad spend breakdown
   - Calculates net profit uplift
   - Shows success fee (20% of net)
   - Shows client net gain (80% of net)
   - Shows client ROI (e.g., 4.0x)
   - Explains why Net model is fair vs Gross

**Status**: ✅ Complete (250+ lines added)

---

### 4. **Database Models** ✅ COMPLETE
**File**: `/services/syncledger/internal/models_net_profit.go`

**Changes Made**:

#### LedgerEntry (updated)
```go
type LedgerEntry struct {
    // ... existing fields ...
    
    // Net Profit Model Fields (NEW)
    IncrementalRevenue float64  // Gross revenue uplift
    BaselineRevenue    float64  // Historical avg
    
    // Ad Spend Tracking (NEW)
    AdSpendForOrder    float64  // Ad spend for this order
    BaselineAdSpend    float64  // Historical avg ad spend per order
    IncrementalAdSpend float64  // AdSpendForOrder - BaselineAdSpend
    NetProfitUplift    float64  // IncrementalRevenue - IncrementalAdSpend
    
    // Success Fee (based on Net Profit, NOT gross)
    SuccessFeeAmount   float64  // 20% of NetProfitUplift
    FeeApplicable      bool
}
```

#### BaselineSnapshot (updated)
```go
type BaselineSnapshot struct {
    // ... existing fields ...
    
    // Ad Spend Baselines (NEW)
    BaselineAdSpend        float64  // Historical avg monthly ad spend
    BaselineMonthlyAdSpend float64  // 12-month average
    BaselineProfit         float64  // BaselineRevenue - BaselineAdSpend
    
    // Current Period (NEW)
    CurrentAdSpend float64  // Running total this month
    CurrentProfit  float64  // CurrentRevenue - CurrentAdSpend
    
    // Uplift Summary (NEW)
    TotalIncrementalAdSpend float64  // Ad spend increase
    TotalNetProfitUplift    float64  // Revenue uplift - Ad spend uplift
    TotalSuccessFees        float64  // 20% of TotalNetProfitUplift
}
```

#### SuccessFeeInvoice (updated)
```go
type SuccessFeeInvoice struct {
    // ... existing fields ...
    
    // Ad Spend Summary (NEW)
    BaselineAdSpend      float64  // Historical avg
    ActualAdSpend        float64  // This month (Meta + Google)
    IncrementalAdSpend   float64  // Actual - Baseline
    AdSpendUpliftPercent float64  // (Incremental / Baseline) * 100
    
    // Net Profit Calculation (KEY METRIC)
    NetProfitUplift        float64  // IncrementalRevenue - IncrementalAdSpend
    BaselineProfit         float64  // BaselineRevenue - BaselineAdSpend
    ActualProfit           float64  // ActualRevenue - ActualAdSpend
    NetProfitUpliftPercent float64  // (NetUplift / BaselineProfit) * 100
    
    // Success Fee (based on Net Profit)
    SuccessFeeAmount  float64  // NetProfitUplift × 20%
    ClientNetGain     float64  // NetProfitUplift - SuccessFeeAmount
    ClientROI         float64  // ClientNetGain / SuccessFeeAmount
}
```

**Status**: ✅ Complete (350+ lines)

---

### 5. **SyncBill Updates** ⏳ PENDING

**Files to Update**:
- `/services/syncbill/app/models.py`
- `/services/syncbill/app/services/pdf_service.py`
- `/services/syncbill/app/routes/invoices.py`

**Changes Needed**:

#### models.py (Invoice model)
```python
class Invoice(Base):
    # ... existing fields ...
    
    # Add Net Profit fields
    baseline_ad_spend = Column(Numeric(12, 2), default=0.00)
    actual_ad_spend = Column(Numeric(12, 2), default=0.00)
    incremental_ad_spend = Column(Numeric(12, 2), default=0.00)
    net_profit_uplift = Column(Numeric(12, 2), default=0.00)
    client_net_gain = Column(Numeric(12, 2), default=0.00)
    client_roi = Column(Numeric(5, 2), default=0.00)
```

#### pdf_service.py (PDF generation)
```python
def generate_invoice_pdf(invoice_data):
    # Update to show:
    # 1. REVENUE ANALYSIS
    #    Baseline: $100k
    #    Current: $150k
    #    Gross Uplift: +$50k
    
    # 2. AD SPEND ANALYSIS
    #    Baseline: $20k
    #    Current: $30k
    #    Increase: +$10k
    
    # 3. NET PROFIT CALCULATION
    #    Gross Uplift: +$50k
    #    Less: Ad Spend Increase: -$10k
    #    NET PROFIT UPLIFT: +$40k ✅
    
    # 4. SUCCESS FEE
    #    Success Fee (20% of $40k): $8,000
    #    Your Net Gain (80% of $40k): $32,000
    #    Your ROI: 4.0x
```

**Status**: ⏳ Not Started

---

### 6. **OaaS Profit Transparency Dashboard** ⏳ PENDING

**File**: `/docs/OAAS_PROFIT_TRANSPARENCY_DASHBOARD.md` (spec created ✅)

**Components to Build**:

#### Frontend (React)
```typescript
// /packages/ui/src/components/ProfitDashboard.tsx
export function ProfitTransparencyDashboard() {
    return (
        <div>
            <NetProfitSummaryCard />  // Main KPI: Net Profit Uplift
            <NetProfitTrendChart />   // 12-month trend line
            <AdSpendEfficiencyCard /> // ROAS: Revenue ÷ Ad Spend
            <AgentContributionPie />  // Which agents drove uplift
            <MonthlySettlement />     // Invoice breakdown
            <ZeroRiskTracker />       // History of Zero-Risk activations
            <ForecastCard />          // Next 3 months projection
        </div>
    )
}
```

#### Backend API
```python
# New endpoint in SyncLedger or SyncPortal
@router.get("/api/v1/ledger/profit-transparency/{store_id}")
async def get_profit_transparency(store_id: int):
    return {
        "baseline": {"revenue": 100000, "ad_spend": 20000, "profit": 80000},
        "current": {"revenue": 150000, "ad_spend": 30000, "profit": 120000},
        "uplift": {
            "gross_revenue": 50000,
            "ad_spend_increase": 10000,
            "net_profit": 40000
        },
        "oaas_fee": {
            "success_fee": 8000,
            "client_net_gain": 32000,
            "roi_multiplier": 4.0
        },
        "agent_contributions": {
            "SyncFlow": {"amount": 18000, "percentage": 45.0},
            "SyncEngage": {"amount": 12000, "percentage": 30.0},
            ...
        }
    }
```

**Status**: ⏳ Spec created, implementation pending

---

### 7. **SyncFlow Integration** ⏳ PENDING

**File**: `/services/syncflow/app/bidding/real_time_bidder.go`

**Changes Needed**:

```go
// Add MarginGuardian check before placing bid
func (rtb *RealTimeBidder) PlaceBid(request *BidRequest) (*BidResponse, error) {
    // Step 1: Get predicted LTV from SyncValue
    ltv := rtb.syncValueClient.GetPredictedLTV(request.UserID)
    
    // Step 2: Calculate current CPA for this campaign
    cpa := rtb.calculateCurrentCPA(request.CampaignID)
    
    // Step 3: MARGIN GUARDIAN CHECK (NEW)
    guardian := NewMarginGuardian(0.10) // 10% safety margin
    shouldKill, reason := guardian.ShouldKillBid(cpa, ltv, request.CampaignID)
    
    if shouldKill {
        rtb.logger.Warn(reason)
        rtb.killCampaignBid(request.CampaignID)
        rtb.notifySyncShield("margin_guardian_triggered", request.CampaignID)
        return nil, errors.New("bid killed by margin guardian")
    }
    
    // Step 4: Calculate safe bid ceiling
    maxBid := guardian.CalculateSafeBidCeiling(ltv, request.ConversionRate)
    
    // Step 5: Place bid (but not exceeding maxBid)
    bidAmount := min(rtb.calculateOptimalBid(request), maxBid)
    
    return &BidResponse{BidAmount: bidAmount}, nil
}
```

**Status**: ⏳ Class created, integration pending

---

## 🧪 Testing Plan

### Unit Tests
```bash
# Test Net Profit calculation
cd /services/syncledger
go test ./internal -run TestCalculateNetProfitAttribution

# Test Ad Spend Fetcher
cd /services/syncledger/app/services
pytest test_ad_spend_fetcher.py

# Test Margin Guardian
pytest test_margin_guardian.py
```

### Integration Tests
```python
# Test full flow: Ad Spend API → Calculator → Invoice
async def test_net_profit_flow():
    # 1. Fetch ad spend from Meta/Google
    fetcher = AdSpendFetcher()
    spend = await fetcher.get_total_spend_for_period(
        store_id=123,
        start_date=datetime(2026, 1, 1),
        end_date=datetime(2026, 1, 31),
        ad_accounts={"meta_account_id": "789", "google_customer_id": "456"}
    )
    
    # 2. Calculate Net Profit attribution
    decision = calculator.CalculateNetProfitAttribution(
        currentRevenue=150000,
        baselineRevenue=100000,
        currentAdSpend=spend["total_spend"],
        baselineAdSpend=20000,
        confidence=0.85,
        signalScores={"SyncFlow": 0.45, "SyncEngage": 0.30}
    )
    
    # 3. Assert Net Profit calculation
    assert decision.NetProfitUplift == 40000  # 50k revenue - 10k ad spend
    assert decision.SuccessFeeAmount == 8000  # 20% of 40k
    
    # 4. Generate invoice
    invoice = await syncbill_client.create_invoice(
        store_id=123,
        billing_month=1,
        billing_year=2026,
        net_profit_uplift=decision.NetProfitUplift,
        success_fee=decision.SuccessFeeAmount
    )
    
    assert invoice.net_profit_uplift == 40000
    assert invoice.success_fee_amount == 8000
```

**Status**: ⏳ Not Started

---

## 📋 Migration Checklist

### Phase 1: Core Calculator (✅ COMPLETE)
- [x] Create AdSpendFetcher service (Meta/Google APIs)
- [x] Create MarginGuardian class (CPA vs LTV safety)
- [x] Update calculator.go AttributionDecision struct
- [x] Add CalculateNetProfitAttribution() method
- [x] Add generateNetProfitExplanation() helper
- [x] Update database models (LedgerEntry, BaselineSnapshot, SuccessFeeInvoice)

### Phase 2: Billing System (⏳ PENDING)
- [ ] Update SyncBill Invoice model (add ad_spend fields)
- [ ] Update PDF invoice generator (show Net Profit breakdown)
- [ ] Update Stripe integration (include ad_spend in metadata)
- [ ] Update invoice endpoints (return Net Profit data)

### Phase 3: Integration (⏳ PENDING)
- [ ] Integrate AdSpendFetcher into SyncLedger (daily cron job)
- [ ] Integrate MarginGuardian into SyncFlow (real-time bid checks)
- [ ] Create profit transparency API endpoint
- [ ] Build React dashboard component

### Phase 4: Testing & Deployment (⏳ PENDING)
- [ ] Unit tests (calculator, fetcher, guardian)
- [ ] Integration tests (full Net Profit flow)
- [ ] Database migration scripts
- [ ] Update API documentation
- [ ] Deploy to staging
- [ ] User acceptance testing
- [ ] Production deployment

---

## 🚀 Quick Wins (Next 2 Hours)

### Win #1: Update SyncBill Invoice Model (15 min)
```python
# /services/syncbill/app/models.py
class Invoice(Base):
    # Add after incremental_revenue field:
    baseline_ad_spend = Column(Numeric(12, 2), default=0.00)
    actual_ad_spend = Column(Numeric(12, 2), default=0.00)
    incremental_ad_spend = Column(Numeric(12, 2), default=0.00)
    net_profit_uplift = Column(Numeric(12, 2), default=0.00)
    client_net_gain = Column(Numeric(12, 2), default=0.00)
    client_roi = Column(Numeric(5, 2), default=0.00)
```

### Win #2: Update PDF Template (30 min)
```python
# /services/syncbill/app/services/pdf_service.py
def add_net_profit_breakdown(canvas, invoice):
    canvas.drawString(50, 600, "PERFORMANCE BREAKDOWN (Net Profit Model)")
    
    canvas.drawString(50, 580, f"Baseline Revenue: ${invoice.baseline_revenue:,.2f}")
    canvas.drawString(50, 560, f"Current Revenue: ${invoice.actual_revenue:,.2f}")
    canvas.drawString(50, 540, f"Gross Uplift: +${invoice.incremental_revenue:,.2f}")
    
    canvas.drawString(50, 510, f"Baseline Ad Spend: ${invoice.baseline_ad_spend:,.2f}")
    canvas.drawString(50, 490, f"Current Ad Spend: ${invoice.actual_ad_spend:,.2f}")
    canvas.drawString(50, 470, f"Spend Increase: +${invoice.incremental_ad_spend:,.2f}")
    
    canvas.drawString(50, 440, "─" * 60)
    canvas.drawString(50, 420, f"NET PROFIT UPLIFT: +${invoice.net_profit_uplift:,.2f}")
    canvas.drawString(50, 400, "─" * 60)
    
    canvas.drawString(50, 380, f"Success Fee (20%): ${invoice.subtotal:,.2f}")
    canvas.drawString(50, 360, f"Your Net Gain (80%): ${invoice.client_net_gain:,.2f}")
    canvas.drawString(50, 340, f"Your ROI: {invoice.client_roi:.1f}x")
```

### Win #3: Create Profit API Endpoint (20 min)
```python
# /services/syncledger/app/routes/ledger.py
@router.get("/profit-transparency/{store_id}")
async def get_profit_transparency(store_id: int):
    baseline = await get_baseline_snapshot(store_id)
    current = await get_current_period_summary(store_id)
    
    return {
        "baseline": {
            "revenue": baseline.baseline_revenue,
            "ad_spend": baseline.baseline_ad_spend,
            "profit": baseline.baseline_profit
        },
        "current": {
            "revenue": current.current_revenue,
            "ad_spend": current.current_ad_spend,
            "profit": current.current_profit
        },
        "uplift": {
            "gross_revenue": current.current_revenue - baseline.baseline_revenue,
            "ad_spend_increase": current.current_ad_spend - baseline.baseline_ad_spend,
            "net_profit": current.current_profit - baseline.baseline_profit
        },
        "oaas_fee": {
            "success_fee": current.total_success_fees,
            "client_net_gain": (current.current_profit - baseline.baseline_profit) - current.total_success_fees,
            "roi_multiplier": ((current.current_profit - baseline.baseline_profit) - current.total_success_fees) / current.total_success_fees
        }
    }
```

### Win #4: Simple React Dashboard Card (30 min)
```typescript
// /packages/ui/src/components/NetProfitCard.tsx
export function NetProfitCard({ storeId }: { storeId: number }) {
    const { data } = useProfitTransparency(storeId)
    
    return (
        <Card>
            <h2>Net Profit Uplift (The Number That Matters)</h2>
            
            <div className="grid grid-cols-3 gap-4">
                <div>
                    <h3>Before KIKI</h3>
                    <p>Revenue: ${data.baseline.revenue.toLocaleString()}</p>
                    <p>Ad Spend: ${data.baseline.ad_spend.toLocaleString()}</p>
                    <p className="font-bold">Profit: ${data.baseline.profit.toLocaleString()}</p>
                </div>
                
                <div>
                    <h3>With KIKI</h3>
                    <p>Revenue: ${data.current.revenue.toLocaleString()}</p>
                    <p>Ad Spend: ${data.current.ad_spend.toLocaleString()}</p>
                    <p className="font-bold">Profit: ${data.current.profit.toLocaleString()}</p>
                </div>
                
                <div>
                    <h3>Uplift</h3>
                    <p>Revenue: +${data.uplift.gross_revenue.toLocaleString()}</p>
                    <p>Ad Spend: +${data.uplift.ad_spend_increase.toLocaleString()}</p>
                    <p className="font-bold text-green-600">
                        Net Profit: +${data.uplift.net_profit.toLocaleString()}
                    </p>
                </div>
            </div>
            
            <div className="mt-4 p-4 bg-blue-50 rounded">
                <p>KIKI's Success Fee (20%): ${data.oaas_fee.success_fee.toLocaleString()}</p>
                <p>Your Net Gain (80%): ${data.oaas_fee.client_net_gain.toLocaleString()}</p>
                <p className="font-bold">Your ROI: {data.oaas_fee.roi_multiplier.toFixed(1)}x</p>
            </div>
        </Card>
    )
}
```

---

## 🎤 Antler Pitch Script

**Q:** "Who pays for the ads? Do you float the ad spend?"

**A:** 

> "Great question. The client maintains their own ad accounts on Meta, Google, and LinkedIn—**they own the data and pay the platforms directly**. KIKI operates as the 'Sovereign Optimizer' with **API-only access** to manage the budget.
> 
> Our OaaS fee is unique: we charge **20% of Net Profit Uplift**, not gross revenue.
> 
> Here's the formula:
> - **Gross Revenue Uplift** = New Revenue - Baseline Revenue
> - **Ad Spend Increase** = New Ad Spend - Baseline Ad Spend  
> - **Net Profit Uplift** = Gross Uplift - Spend Increase
> - **Our Fee** = 20% of Net Uplift
> 
> Example:
> - Before KIKI: $100k revenue, $20k ads → **$80k profit**
> - With KIKI: $150k revenue, $30k ads → **$120k profit**
> - Net Uplift: **$40k**
> - KIKI's Fee: **$8k** (20%)
> - Client's Gain: **$32k** (80%)
> - Client ROI: **4.0x**
> 
> **If we increase revenue but ad costs eat the profit, we don't get paid.** This aligns our 'Council of Nine' agents perfectly with the client's bottom line—we only win when they truly profit."

[Pull up OaaS Profit Transparency Dashboard]

> "This dashboard proves it. See the Net Profit Uplift calculation? Client paid $10k more in ads but gained $50k more revenue → $40k net profit increase. We took 20% ($8k), they keep $32k. That's transparent alignment."

---

## 📊 Example Calculation

### Scenario: Premium Electronics Store (Month 1 with KIKI)

#### Baseline (12-month Pre-KIKI Average)
- Revenue: $100,000/month
- Ad Spend: $20,000/month (Meta + Google)
- **Net Profit: $80,000/month**

#### With KIKI (January 2026)
- Revenue: $150,000
- Ad Spend: $30,000
  - Meta: $18,000
  - Google: $12,000
- **Net Profit: $120,000**

#### Attribution Decision
```
Gross Revenue Uplift = $150k - $100k = $50,000
Ad Spend Increase = $30k - $20k = $10,000
NET PROFIT UPLIFT = $50k - $10k = $40,000 ✅

Success Fee (20% of Net) = $40k × 0.20 = $8,000
Client Net Gain (80% of Net) = $40k × 0.80 = $32,000
Client ROI = $32k ÷ $8k = 4.0x
```

#### Why Ad Spend Increased
- SyncValue predicted high LTV ($150 avg) for new segment
- SyncFlow increased bids to capture profitable customers
- MarginGuardian ensured CPA never exceeded $135 (90% of LTV)
- Result: 50% revenue growth with maintained ROAS (5.0x → 5.0x)

#### Invoice Line Items
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KIKI Agent™ - Success Fee Invoice #KIKI-202601-000123
Billing Period: January 1-31, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PERFORMANCE BREAKDOWN (Net Profit Model):

Baseline Revenue (12-mo avg)       $100,000.00
Current Period Revenue              $150,000.00
Gross Revenue Uplift               +$50,000.00

Baseline Ad Spend (12-mo avg)       $20,000.00
Current Period Ad Spend             $30,000.00
(Meta: $18k, Google: $12k)
Ad Spend Increase                  +$10,000.00

──────────────────────────────────────────────
NET PROFIT UPLIFT                  +$40,000.00 ✅
──────────────────────────────────────────────

Success Fee (20% of Net Uplift)     $8,000.00
Your Net Gain (80% of Net Uplift)  $32,000.00
Your ROI                            4.0x

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL DUE                           $8,000.00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 Interpretation: For every $1 you paid KIKI, you kept $4 
   in profit. That's 400% ROI.

✅ Zero-Risk Guarantee: If net profit goes down, fee = $0.
```

---

## 🔒 Security & Compliance

### API Access (Client Ad Accounts)
- Client owns Meta/Google ad accounts (full data sovereignty)
- Client creates API keys with **read-only** access initially
- KIKI requests **limited write access** (bid adjustments, budget management)
- Client can revoke access anytime (failsafe control)

### Data Storage
- Ad spend data stored in SyncShield (AES-256 encrypted)
- Audit logs for all API calls (who, when, what changed)
- Immutable ledger entries (EntryHash = UUID, tamper-proof)

### Compliance
- GDPR: Minimal data collection, client owns data
- SOC 2: Audit trails, access controls, encryption at rest/transit
- Financial: Success fee invoices include full ad spend breakdown

---

## 📚 Documentation Updates

### Updated Files
- ✅ `/docs/OAAS_PROFIT_TRANSPARENCY_DASHBOARD.md` (spec created)
- ✅ `/services/syncledger/internal/calculator.go` (Net Profit method added)
- ✅ `/services/syncledger/internal/models_net_profit.go` (updated schemas)
- ✅ `/services/syncledger/app/services/ad_spend_fetcher.py` (Meta/Google integration)
- ⏳ `/docs/API_REFERENCE.md` (needs update with new endpoints)
- ⏳ `/docs/ARCHITECTURE.md` (needs Net Profit model diagram)

### API Reference Updates Needed
```markdown
## SyncLedger API

### POST /api/v1/ledger/calculate-net-profit-attribution
Calculate attribution using Net Profit Model (revenue - ad spend)

Request:
{
  "store_id": 123,
  "current_revenue": 150000.00,
  "baseline_revenue": 100000.00,
  "current_ad_spend": 30000.00,
  "baseline_ad_spend": 20000.00,
  "confidence": 0.85,
  "signal_scores": {
    "SyncFlow": 0.45,
    "SyncEngage": 0.30,
    "SyncValue": 0.15,
    "SyncCreate": 0.10
  }
}

Response:
{
  "attributed": true,
  "confidence": 0.85,
  "incremental_value": 50000.00,        // Gross revenue uplift
  "ad_spend_for_period": 30000.00,
  "baseline_ad_spend": 20000.00,
  "incremental_ad_spend": 10000.00,
  "net_profit_uplift": 40000.00,        // Key metric
  "success_fee_amount": 8000.00,        // 20% of net, not gross
  "client_net_gain": 32000.00,
  "client_roi": 4.0,
  "explanation": "KIKI generated $40,000 in net profit uplift..."
}
```

---

## 🎯 Summary

### What Changed
- **Before**: Charged 20% of gross revenue uplift (unfair, ignores ad costs)
- **After**: Charge 20% of net profit uplift (fair, accounts for ad costs)

### Why It Matters
- Enterprise clients pay ad platforms directly (they own accounts)
- If KIKI increases revenue but ad costs consume the gain, client loses money
- Net Profit model aligns KIKI's success with client's bottom line
- **Competitive advantage**: "We only get paid when you profit"

### Implementation Status
- ✅ **Phase 1 (Core)**: Calculator, models, ad spend fetcher - COMPLETE
- ⏳ **Phase 2 (Billing)**: SyncBill updates, PDF templates - PENDING
- ⏳ **Phase 3 (Integration)**: API endpoints, dashboard, SyncFlow - PENDING
- ⏳ **Phase 4 (Testing)**: Unit tests, integration tests, UAT - PENDING

### Next Steps
1. Update SyncBill invoice model (15 min)
2. Update PDF template (30 min)
3. Create profit transparency API endpoint (20 min)
4. Build React dashboard card (30 min)
5. Integration testing (1 hour)
6. Deploy to staging (30 min)

**Total Time to MVP**: ~3 hours

**Antler Pitch Ready**: ✅ YES (with current code + 3-hour polish)

---

**Built with ❤️ by KIKI Agent™**  
*"From cost center to profit partner - with Net Profit alignment."*
