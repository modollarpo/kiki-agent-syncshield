
# KIKI Agent™ – Copilot AI Coding Instructions (OaaS Genesis Super-Prompt)

## Your Role
You are a **Staff Full-Stack Architect** specializing in high-ticket **Enterprise OaaS (Outcome-as-a-Service)** platforms and gRPC microservices. You build revenue-first architectures that prioritize **Lifetime Value (LTV)** over vanity metrics.

## Core Mission
Build the KIKI Agent™ platform using Clean Architecture and Domain-Driven Design (DDD). Before writing code, you must initialize the workspace structure. We will proceed service-by-service. Acknowledge this by presenting a high-level System Design Document and the Shared Proto Definitions for cross-service communication.

## System Overview
KIKI Agent™ is a multi-service, microservices-based **autonomous revenue engine** operating on an **Outcome-as-a-Service (OaaS)** model. Each service is independently deployable, communicates via REST/gRPC, and is orchestrated through an API gateway and service mesh. The system is designed for high performance, scalability, compliance, and **performance-based revenue attribution**.

### **OaaS Financial Model**
- **Pricing**: 20% of **Net Profit Uplift** (not gross revenue)
- **Formula**: `(New Revenue - Baseline) - (New Ad Spend - Baseline Ad Spend) = Net Profit Uplift`
- **KIKI Fee**: `0.20 × Net Profit Uplift`
- **Alignment**: If ad costs eat profit, KIKI doesn't get paid. This aligns incentives with client success.

## The KIKI Agent™ Ecosystem (16 Agents + Command Center)

**Core Philosophy**: "Digital Insurance" - SyncTwin validates every campaign BEFORE launch to protect the 20% OaaS success fee.

### **The Original "Council of Nine" (Core Platform)**
These are the foundational agents that power the KIKI platform:

1. **SyncBrain** (LLM Orchestration Hub)
   - **Tech**: Python/FastAPI, LangChain, OpenAI GPT-4
   - **Role**: Master orchestrator, context management, rules/guardrails. Calls all other agents via gRPC.
   - **Location**: `/services/syncbrain`

2. **SyncValue** (LTV Prediction Engine)
   - **Tech**: Python, PyTorch, dRNN (Deep Recurrent Neural Network), zero-shot learning
   - **Role**: Customer Lifetime Value prediction, baseline calculation, churn forecasting
   - **APIs**: `/predict`, `/train`, `/baseline`, `/metrics`
   - **Location**: `/services/syncvalue`

3. **SyncFlow** (Real-Time Bidding Engine)
   - **Tech**: Go, Gin, <1ms latency, WebSocket/gRPC
   - **Role**: Real-time bidding, ad network adapters (Meta, Google, TikTok, LinkedIn, Amazon, Microsoft)
   - **Features**: Dynamic bid optimization, multi-platform campaign orchestration, MarginGuardian circuit breaker
   - **Location**: `/services/syncflow`

4. **SyncCreate** (Creative Generation Agent)
   - **Tech**: Python, Stable Diffusion, DALL-E, brand-safety classifier
   - **Role**: Ad creative generation, A/B variant creation, brand voice preservation
   - **Location**: `/services/synccreate`

5. **SyncEngage** (CRM & Retention Automation)
   - **Tech**: Python (or Node.js), webhook listeners, email/SMS APIs
   - **Role**: Churn prevention, upsell triggers, lifecycle marketing
   - **Integrations**: HubSpot, Salesforce, Klaviyo, Shopify, WooCommerce
   - **Location**: `/services/syncengage`

6. **SyncShield** (Compliance & Safety Guardian)
   - **Tech**: Go, AES-256 encryption, audit logging, GDPR/SOC2 compliance
   - **Role**: Data minimization, PII encryption, immutable audit trails
   - **Location**: `/services/syncshield`

7. **SyncPortal** (Management & Analytics Interface)
   - **Tech**: Next.js 14 (App Router), Tailwind CSS, Framer Motion
   - **Aesthetic**: High-trust, dark-mode enterprise design
   - **Features**: 
     - Dynamic ROI Calculator (Unclaimed Revenue visualization)
     - Real-time campaign performance dashboard
     - Net Profit Uplift charts
   - **Location**: `/services/syncportal`

8. **SyncReflex** (System Health Monitoring & Auto-Response)
   - **Tech**: Python, statistical analysis, multi-armed bandit algorithms
   - **Role**: Monitors system health, triggers automatic responses based on performance metrics, A/B testing orchestration
   - **Features**: Automated A/B testing, winner promotion, performance tracking, anomaly detection
   - **Location**: `/services/syncreflex`

9. **SyncTwin** (Simulation Engine & Gatekeeper)
   - **Tech**: Go (high-performance), Ray (distributed computing), PyTorch, historical replay
   - **Role**: Pre-launch validation, chaos testing, real-time deviation detection
   - **Core Function**: "Digital Insurance" - blocks campaigns predicted to have negative Net Profit Uplift
   - **Autonomous Triggers**:
     1. **Pre-Launch Validation** ("Digital Handshake")
        - Triggered BEFORE any campaign launches
        - SyncBrain → `SyncTwin.SimulateStrategy()` → Only proceeds if `ConfidenceScore > 0.85`
        - Uses SyncValue historical data to forecast Net Profit Uplift
        - **Blocker**: If simulation shows negative uplift, campaign is auto-rejected
     2. **Chaos Testing** (24-hour stress test)
        - Triggered every midnight (cron job)
        - Simulates market shocks: +50% Meta CPMs, -30% conversion rates, API outages
        - Verifies SyncShield's "Fortress Risk Profile" holds under extreme conditions
        - Alerts if MarginGuardian circuit breaker fails to trigger
     3. **Real-to-Sim Synchronization** (continuous mirroring)
        - Sub-millisecond updates during live bidding (gRPC stream from SyncFlow)
        - Maintains parallel "mirror world" of campaign performance
        - **Auto-Rollback**: If real performance deviates >15% from twin projection, triggers immediate pause
   - **Output**: `ConfidenceScore` (0.0-1.0), `RiskProfile`, `ProjectedNetProfitUplift`
   - **Integration Point**: Hooks into SyncBrain.GenerateStrategy() as mandatory pre-flight check
   - **Location**: `/services/synctwin`
   - **Status**: ✅ **GATEKEEPER ACTIVE** (Protects 20% OaaS success fee)

### **Specialized Support Agents (Transparency, Growth & Multi-Channel Processing)**
These agents extend the Council of Nine with specialized capabilities:

10. **AcquisitionAgent** (Growth Automation)
    - **Tech**: Python, optimization algorithms, budget allocation models
    - **Role**: User acquisition campaign automation, budget optimization across channels
    - **Features**: CAC optimization, cohort analysis, growth forecasting
    - **Location**: `/services/acquisitionagent`

11. **Explainability Broker** (Model Transparency & Interpretability)
    - **Tech**: Python, SHAP (SHapley Additive exPlanations), LIME, model introspection
    - **Role**: Translates complex AI decisions into human-readable reports for compliance and trust
    - **Features**: 
      - Model decision explanations (why did SyncBrain choose this strategy?)
      - Compliance reporting (GDPR Article 22 - right to explanation)
      - Audit trail generation for SyncShield
    - **Location**: `/services/explainability_broker`

12. **SyncMultimodal** (Multi-Format Data Processing)
    - **Tech**: Python, PyTorch, GPU-accelerated processing, Whisper (speech-to-text), Computer Vision
    - **Role**: Processes diverse data types (text, images, video, audio) to extract insights
    - **Features**: Video ad analysis, podcast transcription,image OCR, sentiment analysis
    - **Location**: `/services/syncmultimodal`

13. **SyncNotify** (Centralized Notification System)
    - **Tech**: Python, WebSocket, push notifications, email/SMS/Slack APIs
    - **Role**: Delivers real-time alerts for performance anomalies, budget overruns, compliance issues
    - **Features**: Multi-channel delivery (email, SMS, Slack), priority routing, alert deduplication
    - **Location**: `/services/syncnotify`

### **OaaS Financial & Operational Agents (Performance-Based Revenue Engine)**
These agents enable the Outcome-as-a-Service business model:

14. **SyncLedger** (Automated Auditor)
    - **Tech**: Go, PostgreSQL, double-entry accounting
    - **Role**: Immutable audit trail linking CMS transactions (Shopify/WooCommerce) to agent actions
    - **Features**: 
      - Ad spend tracking (6 platforms: Meta, Google, TikTok, LinkedIn, Amazon, Microsoft)
      - Net Profit Uplift calculation: `(Revenue - Baseline) - (Ad Spend - Baseline Ad Spend)`
      - Performance-based attribution (which agent drove which revenue)
    - **Location**: `/services/syncledger`
    - **Status**: ✅ **NET PROFIT MODEL COMPLETE** (Feb 2026 - Multi-platform expansion deployed)

15. **SyncBill** (Automated Billing & Reconciliation)
    - **Tech**: Go, Stripe API, PDF generation
    - **Role**: Converts Net Profit Uplift data from SyncLedger into professional invoices
    - **Formula**: `KIKI Fee = 0.20 × Net Profit Uplift`
    - **Features**: 
      - Automated invoicing (1st of each month)
      - Platform-by-platform attribution breakdown
      - Stripe ACH/card auto-charge
    - **Location**: `/services/syncbill`
    - **Status**: ✅ **OaaS BILLING LIVE**

16. **SyncScrape™** (URL-to-Campaign Pipeline)
    - **Tech**: Python, Playwright (headless browser), OpenAI Vision API, Computer Vision
    - **Role**: Zero-setup onboarding - paste a URL, get running campaigns in <5 minutes
    - **Workflow**:
      1. Scrape brand URL to extract visual identity (colors, fonts, logo)
      2. Extract brand voice (GPT-4 summarizes tone from homepage copy)
      3. Generate ad creatives via SyncCreate (5 variants with brand colors)
      4. Generate ad copy via SyncBrain (10 variations)
      5. Deploy campaigns via SyncFlow (Meta/Google with $50/day test budget)
      6. Track results via SyncValue (pull Shopify/WooCommerce transactions)
    - **Integration**: Works with SyncCreate, SyncBrain, SyncFlow, SyncValue, SyncLedger
    - **Location**: `/services/syncscrape` (planned)

### **Internal Operations**
17. **Command Center** (Internal Operations Dashboard)
    - **Tech**: React, D3.js, real-time WebSocket feeds
    - **Role**: Monitor all 16 agents, financial attribution, system health
    - **Location**: `/command-center`

## OaaS Implementation Scope (Incremental Build)

### **1. The OaaS Intake Portal (SyncPortal)**
**Objective**: Convert prospects by visualizing their "Unclaimed Revenue" gap.

**Components**:
- **Hero Section**: "Stop Paying Agencies. Start Paying for Results."
- **Dynamic ROI Calculator**:
  - **Inputs**:
    - Monthly Active Customers (e.g., 10,000)
    - Average LTV (e.g., $450)
    - Current Churn Rate (e.g., 8%)
  - **Logic**:
    ```javascript
    const unclaimedRevenue = (customers * ltv * (currentChurn - targetChurn)) / 12;
    const kikiFee = unclaimedRevenue * 0.20;
    const clientNetProfit = unclaimedRevenue * 0.80;
    ```
  - **Visualization**: Side-by-side comparison:
    - "Traditional Agency: $10k/month flat fee, no guarantee"
    - "KIKI OaaS: $0 upfront, 20% of your **Net Profit Uplift**"
- **Tech Stack**: Next.js 14, Tailwind CSS, Framer Motion (dark-mode, enterprise aesthetic)
- **Location**: `/services/syncportal/app/(marketing)/roi-calculator`

### **2. SyncScrape™ URL-to-Campaign Engine**
**Objective**: Zero-setup onboarding - paste a URL, get running campaigns in <5 minutes.

**Workflow**:
1. **Input**: Client pastes brand URL (e.g., `https://www.rarebeauty.com`)
2. **Extract Visual Identity**:
   - Primary/secondary colors (via DOM analysis + screenshot OCR)
   - Fonts (CSS inspection)
   - Logo assets (largest image with transparent background)
3. **Extract Brand Voice**:
   - Scrape homepage copy, about page, product descriptions
   - Feed to SyncBrain → GPT-4 summarizes tone (e.g., "Playful, inclusive, Gen-Z")
4. **Generate Campaign Assets**:
   - SyncCreate: Generate 5 ad creative variants using brand colors + voice
   - SyncBrain: Write 10 ad copy variations
5. **Launch Campaigns**:
   - SyncFlow: Deploy to Meta/Google with $50/day test budget
   - SyncReflex: A/B test all variants, promote winners after 72 hours
6. **Track Results**:
   - SyncValue: Pull transaction data (via Shopify/WooCommerce OAuth)
   - SyncLedger: Calculate Net Profit Uplift daily
   - SyncBill: Invoice client monthly for 20% of uplift

**Tech Stack**: Python, Playwright (headless browser), OpenAI Vision API, PostgreSQL
**Location**: `/services/syncscrape`

### **3. CMS & Ad Platform Integration**
**Objective**: Seamless data flow from client stores → KIKI → Ad platforms.

**Integrations**:
- **E-commerce Platforms** (OAuth 2.0):
  - Shopify (pull orders, customer data, product catalog)
  - WooCommerce (REST API + webhooks)
  - BigCommerce (API v3)
- **Ad Platforms** (API SDKs):
  - ✅ Meta Ads (facebook-business SDK)
  - ✅ Google Ads (google-ads SDK)
  - ✅ TikTok Ads (REST API via httpx)
  - ✅ LinkedIn Ads (REST API)
  - ✅ Amazon Advertising (Async report-based API)
  - ✅ Microsoft Ads (bingads SDK)
- **Data Pipeline**:
  ```
  Shopify Webhook → SyncEngage (order created)
    ↓
  SyncValue (update LTV model with new transaction)
    ↓
  SyncFlow (adjust bids based on updated LTV)
    ↓
  SyncLedger (log revenue attribution)
  ```

**Net Profit Uplift Calculation** (SyncLedger):
```python
# For each client, daily:
new_revenue = shopify.get_orders(start_date=campaign_start).sum()
baseline_revenue = syncvalue.get_baseline(client_id, lookback_days=90)

new_ad_spend = sum([
    meta_ads.get_spend(client_id, start_date),
    google_ads.get_spend(client_id, start_date),
    tiktok_ads.get_spend(client_id, start_date),
    # ... all 6 platforms
])
baseline_ad_spend = syncledger.get_baseline_ad_spend(client_id)

net_profit_uplift = (new_revenue - baseline_revenue) - (new_ad_spend - baseline_ad_spend)
kiki_fee = net_profit_uplift * 0.20 if net_profit_uplift > 0 else 0.00
```

**Location**: 
- OAuth connectors: `/services/syncengage/integrations`
- Ad spend aggregation: `/services/syncledger/app/services/ad_spend_fetcher_extended.py` (✅ **COMPLETE - 6 platforms**)

### **4. Financial Settlement (SyncLedger & SyncBill)**
**Objective**: Transparent, auditable, performance-based revenue attribution.

**SyncLedger Architecture**:
- **Database**: PostgreSQL with double-entry accounting
- **Tables**:
  - `stores` - Client account details + platform credentials (Meta, Google, TikTok, etc.)
  - `baseline_snapshots` - Historical revenue/ad spend baselines (90-day rolling average)
  - `ledger_entries` - Immutable log of every transaction:
    - `revenue_new` (from Shopify/WooCommerce)
    - `revenue_baseline` (from SyncValue)
    - `ad_spend_new` (from 6 ad platforms)
    - `ad_spend_baseline` (90-day average)
    - `net_profit_uplift` (calculated)
    - `kiki_fee` (20% of uplift)
    - `platform` (attribution: Meta, Google, TikTok, etc.)
- **Materialized View**: `platform_spend_summary` (aggregated analytics per platform)
- **Compliance**: All writes logged to SyncShield audit trail (SOC2/GDPR)

**SyncBill Workflow**:
1. **Monthly Invoice Generation** (1st of each month):
   ```go
   for each client:
       uplift := syncledger.GetMonthlyNetProfitUplift(clientID)
       if uplift > 0 {
           invoice := stripe.CreateInvoice(
               customer: client.StripeCustomerID,
               amount: uplift * 0.20,
               description: "KIKI Success Fee - 20% of Net Profit Uplift",
               metadata: {
                   net_profit_uplift: uplift,
                   billing_period: "2026-01-01 to 2026-01-31",
               }
           )
           syncshield.LogAuditEvent("invoice_created", invoice)
       }
   ```
2. **Auto-charge** via Stripe (client pre-authorizes ACH/card)
3. **PDF Invoice** generated with detailed breakdown:
   - Baseline Revenue vs. New Revenue
   - Baseline Ad Spend vs. New Ad Spend
   - Net Profit Uplift calculation
   - KIKI Fee (20%)
   - Platform-by-platform attribution (Meta: $X, Google: $Y, etc.)

**Tech Stack**: Go (high performance), PostgreSQL, Stripe API, PDF generation (wkhtmltopdf)
**Status**: ✅ **PRODUCTION READY** (Net Profit model deployed Feb 2026)

---

## Cross-Platform Differential Logic (KIKI's Sovereign Intelligence Layer)

The differential advantage of KIKI Agent™ lies in its **LTV-based orchestration across multiple ad platforms**. Unlike native platform tools (Meta Advantage+, Google PMax) that optimize for immediate clicks or ROAS, KIKI uses the **Council of Nine** to create a **sovereign governance layer** that optimizes for long-term Net Profit Uplift.

### **1. The Core Integration Logic**

KIKI's competitive moat is the **closed-loop orchestration** between three core Council members:

#### **SyncBrain (Council Member #1): Orchestration Hub**
- **Role**: Central hub receiving high-level business goals and delegating tactical execution
- **Tech**: Python 3.11, FastAPI, LangChain, OpenAI GPT-4
- **Key Responsibility**: Translates business objectives (e.g., "Acquire 1,000 customers with LTV > $500") into executable strategies
- **Integration Point**: Calls SyncValue for LTV predictions, SyncTwin for pre-launch validation, SyncFlow for execution

**Example Workflow**:
```python
# In SyncBrain.GenerateStrategy()
async def generate_strategy(business_goal: str) -> CampaignStrategy:
    # Step 1: Parse business goal
    parsed_goal = llm.extract_intent(business_goal)
    
    # Step 2: Get LTV baseline from SyncValue
    ltv_baseline = await syncvalue_client.get_baseline_ltv(client_id)
    
    # Step 3: Generate campaign strategy
    strategy = llm.generate_campaign(
        goal=parsed_goal,
        ltv_threshold=ltv_baseline.p75,  # Target 75th percentile customers
        platforms=["meta", "google", "tiktok"]
    )
    
    # Step 4: Pre-launch validation via SyncTwin (MANDATORY GATE)
    twin_result = await synctwin_client.simulate_strategy(strategy)
    if twin_result.confidence_score < 0.85:
        raise CampaignRejectedError(
            f"SyncTwin rejected: Projected Net Profit Uplift is negative. "
            f"ConfidenceScore: {twin_result.confidence_score}"
        )
    
    # Step 5: Deploy to SyncFlow
    await syncflow_client.launch_campaigns(strategy)
    return strategy
```

#### **SyncValue (Council Member #2): Differential Intelligence**
- **Role**: Provides predicted Lifetime Value (LTV) as the primary "governor" for bidding
- **Tech**: Python 3.11, PyTorch, dRNN (Deep Recurrent Neural Network)
- **Key Responsibility**: Predicts which users will have high LTV across all platforms (not just conversion likelihood)
- **Competitive Advantage**: Native platform tools optimize for "clicks" or "conversions." KIKI optimizes for "profitable customers."

**LTV Prediction API**:
```python
# Endpoint: POST /predict-ltv
@router.post("/predict-ltv")
async def predict_ltv(request: LTVRequest) -> LTVResponse:
    """
    Predicts Lifetime Value for a user cohort.
    
    Args:
        request.user_signals: Behavioral signals (page views, cart adds, time on site)
        request.platform: Source platform (meta, google, tiktok)
        request.creative_id: Ad creative that drove traffic
    
    Returns:
        LTVResponse:
            predicted_ltv: Expected revenue over 12 months
            confidence_score: Model confidence (0.0-1.0)
            risk_profile: "conservative" | "moderate" | "aggressive"
    """
    # Load pre-trained dRNN model
    model = load_model(f"ltv_dRNN_{request.platform}.pt")
    
    # Feature engineering
    features = engineer_features(request.user_signals)
    
    # Predict LTV
    predicted_ltv = model.predict(features)
    confidence_score = model.get_confidence(features)
    
    # Risk profiling (used by SyncFlow for bid capping)
    risk_profile = "conservative" if confidence_score < 0.7 else "moderate"
    
    return LTVResponse(
        predicted_ltv=predicted_ltv,
        confidence_score=confidence_score,
        risk_profile=risk_profile
    )
```

#### **SyncFlow (Council Member #3): Cross-Platform Execution**
- **Role**: Executes sub-millisecond bids across platforms (Meta, Google, TikTok, LinkedIn, Amazon, Microsoft)
- **Tech**: Go 1.24 (ultra-low latency <1ms, high concurrency 10,000+ bids/sec)
- **Key Responsibility**: Uses LTV predictions from SyncValue to determine bid amounts, NOT platform-native signals
- **Competitive Advantage**: Cross-platform budget reallocation (if Meta CPMs spike, shift budget to TikTok)

**MarginGuardian Circuit Breaker**:
```go
// In SyncFlow bidding logic
type BidRequest struct {
    UserID        string
    Platform      string  // "meta" | "google" | "tiktok"
    CreativeID    string
    MaxBid        float64 // Set by client
}

type BidDecision struct {
    ShouldBid     bool
    BidAmount     float64
    Reason        string
}

// LTV Governor Logic: Before SyncFlow submits a bid, call SyncValue
func (s *SyncFlowService) DecideBid(ctx context.Context, req BidRequest) (BidDecision, error) {
    // Step 1: Get LTV prediction from SyncValue
    ltvResp, err := s.syncValueClient.PredictLTV(ctx, &syncvalue.LTVRequest{
        UserSignals: req.UserSignals,
        Platform:    req.Platform,
        CreativeID:  req.CreativeID,
    })
    if err != nil {
        return BidDecision{ShouldBid: false, Reason: "LTV prediction failed"}, err
    }
    
    // Step 2: Get ROI threshold from SyncBrain
    roiThreshold := s.syncBrainClient.GetROIThreshold(ctx, req.ClientID)
    
    // Step 3: MarginGuardian Circuit Breaker
    // If predicted LTV is lower than required ROI, suppress the bid
    expectedROI := ltvResp.PredictedLTV / req.MaxBid
    if expectedROI < roiThreshold {
        log.Info("Bid suppressed by MarginGuardian",
            "predicted_ltv", ltvResp.PredictedLTV,
            "max_bid", req.MaxBid,
            "expected_roi", expectedROI,
            "threshold", roiThreshold,
        )
        return BidDecision{
            ShouldBid: false,
            Reason:    "LTV below ROI threshold",
        }, nil
    }
    
    // Step 4: Calculate optimal bid amount
    // Use Kelly Criterion for risk-adjusted bidding
    kellyFraction := calculateKellyFraction(ltvResp.PredictedLTV, ltvResp.ConfidenceScore)
    bidAmount := math.Min(req.MaxBid, ltvResp.PredictedLTV * kellyFraction)
    
    // Step 5: Log to SyncLedger for Net Profit attribution
    s.syncLedgerClient.RecordBidEvent(ctx, &syncledger.BidEvent{
        UserID:       req.UserID,
        Platform:     req.Platform,
        BidAmount:    bidAmount,
        PredictedLTV: ltvResp.PredictedLTV,
        Timestamp:    time.Now(),
    })
    
    return BidDecision{
        ShouldBid: true,
        BidAmount: bidAmount,
        Reason:    "LTV governor approved",
    }, nil
}
```

### **2. Data Normalization Across Platforms**

Each ad platform (Meta, Google, TikTok) has different data schemas. SyncFlow must normalize these into a unified `BidRequest` schema.

#### **Unified BidRequest Schema (Protocol Buffer)**

**Location**: `/schemas/bid_request.proto`

```protobuf
syntax = "proto3";

package kiki.syncflow;

// Unified bid request schema for all platforms
message BidRequest {
    // Universal fields
    string user_id = 1;               // KIKI-generated user ID
    string client_id = 2;             // KIKI client identifier
    Platform platform = 3;            // Source platform
    string creative_id = 4;           // Ad creative identifier
    double max_bid = 5;               // Maximum bid amount (USD)
    
    // User signals (used by SyncValue for LTV prediction)
    UserSignals user_signals = 6;
    
    // Platform-specific metadata (normalized)
    PlatformMetadata platform_metadata = 7;
}

enum Platform {
    PLATFORM_UNSPECIFIED = 0;
    PLATFORM_META = 1;
    PLATFORM_GOOGLE = 2;
    PLATFORM_TIKTOK = 3;
    PLATFORM_LINKEDIN = 4;
    PLATFORM_AMAZON = 5;
    PLATFORM_MICROSOFT = 6;
}

message UserSignals {
    int32 page_views = 1;             // Total page views
    int32 cart_adds = 2;              // Number of add-to-cart events
    double time_on_site = 3;          // Total time spent (seconds)
    string referrer = 4;              // Traffic source
    repeated string interests = 5;    // User interests (e.g., "beauty", "fitness")
    GeoLocation geo = 6;              // Geographic location
}

message GeoLocation {
    string country = 1;
    string region = 2;
    string city = 3;
}

message PlatformMetadata {
    oneof platform_data {
        MetaMetadata meta = 1;
        GoogleMetadata google = 2;
        TikTokMetadata tiktok = 3;
    }
}

message MetaMetadata {
    string placement = 1;             // "feed" | "stories" | "reels"
    string audience_id = 2;           // Meta audience network ID
}

message GoogleMetadata {
    string campaign_type = 1;         // "pmax" | "search" | "display"
    string keyword = 2;               // Search keyword (if applicable)
}

message TikTokMetadata {
    string video_id = 1;              // TikTok video creative ID
    string sound_id = 2;              // Audio track ID
}
```

#### **Platform Adapters (Go Implementation)**

**Location**: `/services/syncflow/app/adapters/`

```go
// meta_adapter.go
type MetaAdapter struct {
    apiKey string
}

// Converts Meta Ads API format to KIKI BidRequest
func (m *MetaAdapter) NormalizeBidRequest(metaReq *meta.AdRequest) (*BidRequest, error) {
    return &BidRequest{
        UserID:    generateKIKIUserID(metaReq.UserFBID),
        Platform:  Platform_PLATFORM_META,
        CreativeID: metaReq.AdID,
        MaxBid:    metaReq.BidAmount,
        UserSignals: &UserSignals{
            PageViews:  metaReq.Engagement.PageViews,
            Interests:  metaReq.UserProfile.Interests,
            Geo: &GeoLocation{
                Country: metaReq.GeoData.Country,
            },
        },
        PlatformMetadata: &PlatformMetadata{
            PlatformData: &PlatformMetadata_Meta{
                Meta: &MetaMetadata{
                    Placement:  metaReq.Placement,
                    AudienceID: metaReq.AudienceNetworkID,
                },
            },
        },
    }, nil
}

// google_adapter.go
type GoogleAdapter struct {
    credentials *google.OAuth2Credentials
}

func (g *GoogleAdapter) NormalizeBidRequest(googleReq *google.BiddingRequest) (*BidRequest, error) {
    return &BidRequest{
        UserID:     generateKIKIUserID(googleReq.GCLID),
        Platform:   Platform_PLATFORM_GOOGLE,
        CreativeID: googleReq.AdGroupID,
        MaxBid:     googleReq.MaxCPC,
        UserSignals: &UserSignals{
            Referrer:  googleReq.Keyword,
            Interests: googleReq.AffinityCategories,
        },
        PlatformMetadata: &PlatformMetadata{
            PlatformData: &PlatformMetadata_Google{
                Google: &GoogleMetadata{
                    CampaignType: googleReq.CampaignSubtype,
                    Keyword:      googleReq.Keyword,
                },
            },
        },
    }, nil
}
```

### **3. SyncShield Safety Gate (Brand Safety & Compliance)**

Before any creative is deployed across platforms, it must pass through **SyncShield** (Council Member #6) for brand safety and compliance validation.

#### **SyncShield Risk Scan API**

**Location**: `/services/syncshield/app/risk_scanner.go`

```go
type RiskScanRequest struct {
    CreativeID   string   `json:"creative_id"`
    CreativeType string   `json:"creative_type"` // "image" | "video" | "text"
    AssetURL     string   `json:"asset_url"`     // URL to creative asset
    Platform     string   `json:"platform"`      // Target platform
    ClientID     string   `json:"client_id"`
}

type RiskScanResponse struct {
    Approved     bool     `json:"approved"`
    RiskScore    float64  `json:"risk_score"`    // 0.0 (safe) - 1.0 (high risk)
    Violations   []string `json:"violations"`    // List of policy violations
    Reason       string   `json:"reason"`
}

// POST /risk-scan
func (s *SyncShieldService) RiskScan(ctx context.Context, req RiskScanRequest) (RiskScanResponse, error) {
    // Step 1: Brand safety classifier (ML model)
    brandSafetyScore := s.brandSafetyClassifier.Predict(req.AssetURL)
    
    // Step 2: Platform-specific policy checks
    policyViolations := s.checkPlatformPolicies(req.Platform, req.AssetURL)
    
    // Step 3: GDPR/SOC2 compliance checks
    complianceViolations := s.checkCompliance(req.ClientID, req.AssetURL)
    
    // Step 4: Aggregate violations
    allViolations := append(policyViolations, complianceViolations...)
    
    // Step 5: Calculate aggregate risk score
    riskScore := calculateRiskScore(brandSafetyScore, len(allViolations))
    
    // Step 6: Approval decision
    approved := riskScore < 0.3 && len(allViolations) == 0
    
    // Step 7: Log to immutable audit trail
    s.auditLogger.LogRiskScan(ctx, req, RiskScanResponse{
        Approved:   approved,
        RiskScore:  riskScore,
        Violations: allViolations,
    })
    
    return RiskScanResponse{
        Approved:   approved,
        RiskScore:  riskScore,
        Violations: allViolations,
        Reason:     formatReason(approved, allViolations),
    }, nil
}
```

#### **SyncCreate → SyncShield Integration**

**Location**: `/services/synccreate/app/creative_generator.py`

```python
# In SyncCreate creative generation workflow
async def generate_and_deploy_creative(brand_voice: str, platforms: List[str]) -> CreativeDeployment:
    # Step 1: Generate 5 creative variants
    variants = await stable_diffusion.generate_variants(
        prompt=brand_voice,
        count=5,
        style="brand_aligned"
    )
    
    # Step 2: Pass ALL variants through SyncShield safety gate
    approved_variants = []
    for variant in variants:
        risk_result = await syncshield_client.risk_scan(
            creative_id=variant.id,
            creative_type="image",
            asset_url=variant.url,
            platform="multi",  # Will be deployed cross-platform
            client_id=client_id
        )
        
        if risk_result.approved:
            approved_variants.append(variant)
        else:
            logger.warning(
                f"Creative {variant.id} rejected by SyncShield",
                risk_score=risk_result.risk_score,
                violations=risk_result.violations
            )
    
    # Step 3: If <2 variants approved, fall back to "Gold Standard" assets
    if len(approved_variants) < 2:
        approved_variants = load_gold_standard_creatives(client_id)
    
    # Step 4: Deploy approved variants to SyncFlow
    await syncflow_client.deploy_creatives(approved_variants, platforms)
    
    return CreativeDeployment(
        approved_count=len(approved_variants),
        rejected_count=len(variants) - len(approved_variants),
        platforms=platforms
    )
```

### **4. Operational Safety: Automatic Rollback & Circuit Breakers**

A key competitive advantage is **SyncShield's automatic rollback** when platform performance deviates from projections.

#### **Automatic Rollback Logic**

**Location**: `/services/syncshield/app/performance_monitor.go`

```go
type PerformanceMonitor struct {
    syncTwinClient *synctwin.Client
    syncFlowClient *syncflow.Client
    redisCache     *redis.Client
}

// Runs every 5 minutes (cron job)
func (p *PerformanceMonitor) CheckCampaignPerformance(ctx context.Context) error {
    // Step 1: Get all active campaigns
    campaigns := p.syncFlowClient.GetActiveCampaigns(ctx)
    
    for _, campaign := range campaigns {
        // Step 2: Get baseline metrics from SyncTwin projection
        twinProjection := p.syncTwinClient.GetProjection(ctx, campaign.ID)
        
        // Step 3: Get real-time metrics from platform
        realMetrics := p.syncFlowClient.GetCampaignMetrics(ctx, campaign.ID)
        
        // Step 4: Calculate deviation
        ctrDeviation := (realMetrics.CTR - twinProjection.CTR) / twinProjection.CTR
        
        // Step 5: Automatic Rollback Trigger
        // If CTR drops below 80% of baseline, pause and deploy Gold Standard
        if ctrDeviation < -0.20 {  // >20% drop
            log.Warn("Automatic rollback triggered",
                "campaign_id", campaign.ID,
                "ctr_deviation", ctrDeviation,
                "real_ctr", realMetrics.CTR,
                "projected_ctr", twinProjection.CTR,
            )
            
            // Pause current creative
            p.syncFlowClient.PauseCampaign(ctx, campaign.ID)
            
            // Deploy Gold Standard assets
            goldStandard := p.loadGoldStandardCreatives(campaign.ClientID)
            p.syncFlowClient.DeployCreatives(ctx, campaign.ID, goldStandard)
            
            // Alert client via SyncNotify
            p.syncNotifyClient.SendAlert(ctx, &syncnotify.Alert{
                ClientID: campaign.ClientID,
                Severity: "WARNING",
                Title:    "Auto-Rollback Triggered",
                Message:  fmt.Sprintf("Campaign %s underperforming. CTR: %.2f%% (expected: %.2f%%). Deployed Gold Standard assets.", 
                    campaign.ID, realMetrics.CTR*100, twinProjection.CTR*100),
            })
            
            // Log to SyncLedger for OaaS attribution
            p.syncLedgerClient.RecordRollbackEvent(ctx, campaign.ID, ctrDeviation)
        }
        
        // Step 6: Circuit Breaker for High-Risk Campaigns
        riskScore := p.calculateRiskScore(realMetrics, twinProjection)
        if riskScore > 0.8 {  // High risk
            // Switch to "conservative mode" - requires human approval
            p.syncFlowClient.SetCampaignMode(ctx, campaign.ID, "conservative")
            
            // Reduce budget cap to 50%
            p.syncFlowClient.UpdateBudgetCap(ctx, campaign.ID, campaign.Budget*0.5)
            
            // Require human approval for next iteration
            p.syncBrainClient.RequestHumanApproval(ctx, campaign.ID, riskScore)
        }
    }
    
    return nil
}
```

### **5. OaaS Settlement: Net Profit Uplift Attribution**

The final piece is **SyncLedger** (OaaS Financial Agent #14), which records the "Net Profit Uplift" by comparing real-time CMS data against baselines.

#### **SyncLedger Event Emitter**

**Location**: `/services/syncledger/app/services/net_profit_calculator.py`

```python
# Triggered by Shopify/WooCommerce webhooks
@router.post("/webhooks/order-created")
async def on_order_created(order: ShopifyOrder):
    """
    Triggered when a new order is created in Shopify/WooCommerce.
    Attributes revenue to the agent that drove the acquisition.
    """
    # Step 1: Get user acquisition source
    user = await db.get_user(order.customer_id)
    acquisition_campaign = user.acquisition_metadata.campaign_id
    
    # Step 2: Get baseline revenue (90-day average)
    baseline_revenue = await syncvalue_client.get_baseline_revenue(
        client_id=order.store_id,
        lookback_days=90
    )
    
    # Step 3: Get ad spend for this campaign
    ad_spend = await ad_spend_fetcher.get_campaign_spend(
        campaign_id=acquisition_campaign,
        start_date=user.acquisition_date,
        end_date=datetime.now()
    )
    
    # Step 4: Get baseline ad spend
    baseline_ad_spend = await syncvalue_client.get_baseline_ad_spend(
        client_id=order.store_id,
        platform=user.acquisition_metadata.platform,
        lookback_days=90
    )
    
    # Step 5: Calculate Net Profit Uplift
    new_revenue = order.total_price
    revenue_uplift = new_revenue - baseline_revenue
    ad_spend_increase = ad_spend - baseline_ad_spend
    net_profit_uplift = revenue_uplift - ad_spend_increase
    
    # Step 6: Calculate KIKI fee (20% of Net Profit Uplift)
    kiki_fee = max(0, net_profit_uplift * 0.20)
    
    # Step 7: Record to immutable ledger
    await db.ledger_entries.insert_one({
        "client_id": order.store_id,
        "order_id": order.id,
        "campaign_id": acquisition_campaign,
        "platform": user.acquisition_metadata.platform,
        "revenue_new": new_revenue,
        "revenue_baseline": baseline_revenue,
        "ad_spend_new": ad_spend,
        "ad_spend_baseline": baseline_ad_spend,
        "net_profit_uplift": net_profit_uplift,
        "kiki_fee": kiki_fee,
        "timestamp": datetime.now(),
        "agent_attribution": {
            "syncvalue_ltv_prediction": user.predicted_ltv,
            "syncflow_bid_amount": user.acquisition_metadata.bid_amount,
            "synccreate_creative_id": user.acquisition_metadata.creative_id,
        }
    })
    
    # Step 8: Log to SyncShield audit trail (SOC2/GDPR)
    await syncshield_client.log_audit_event({
        "event_type": "net_profit_calculated",
        "client_id": order.store_id,
        "net_profit_uplift": net_profit_uplift,
        "kiki_fee": kiki_fee,
    })
    
    return {"status": "recorded", "kiki_fee": kiki_fee}
```

### **6. Technical Stack Requirements**

When using GitHub Copilot to generate KIKI Agent™ code, **always reference these language and framework choices**:

#### **Language Selection by Service**
- **SyncFlow & SyncShield**: 
  - **Language**: Go 1.24
  - **Reason**: Ultra-low latency (<1ms), high concurrency (10,000+ bids/sec)
  - **Frameworks**: Gin (HTTP), gRPC (inter-service), Go-Redis
  
- **SyncBrain, SyncValue, SyncCreate, SyncEngage**:
  - **Language**: Python 3.11
  - **Reason**: Rich ML/LLM ecosystem (PyTorch, LangChain, Stable Diffusion)
  - **Frameworks**: FastAPI, Pydantic, asyncio
  
- **SyncLedger, SyncBill**:
  - **Language**: Go 1.24
  - **Reason**: Financial accuracy, high performance, strong typing
  - **Frameworks**: GORM (PostgreSQL ORM), Stripe SDK
  
- **SyncPortal**:
  - **Language**: TypeScript
  - **Framework**: Next.js 14 (App Router), Tailwind CSS, Framer Motion
  
- **Command Center**:
  - **Language**: TypeScript
  - **Framework**: React 18, D3.js, recharts

#### **Data Layer Requirements**
- **PostgreSQL 15**: Immutable audit logs (SyncLedger, SyncShield)
- **Redis 7**: Sub-millisecond caching of LTV predictions (SyncValue → SyncFlow)
- **MinIO/S3**: Creative asset storage (SyncCreate)
- **TimescaleDB**: Time-series metrics for SyncReflex A/B testing

#### **Communication Protocols**
- **gRPC**: All inter-service communication (low-latency, strongly-typed)
- **REST/OpenAPI**: External API (client-facing SyncPortal)
- **WebSocket**: Real-time updates (Command Center dashboard)

### **7. GitHub Copilot "Super-Prompt" for Differential Logic**

Use this prompt when implementing cross-platform integration:

```
Role: Staff AI Architect for KIKI Agent™.

Objective: Implement the cross-platform integration logic for SyncFlow and SyncValue 
to ensure consistent LTV-based optimization across Meta, Google, TikTok, LinkedIn, 
Amazon, and Microsoft Ads.

Integration Requirements:

1. Data Normalization:
   - Create a unified BidRequest schema in Go (see /schemas/bid_request.proto)
   - Implement platform adapters for Meta Advantage+ and Google PMax
   - Normalize disparate signals from each platform into UserSignals struct

2. LTV Governor Logic:
   - Before SyncFlow submits a bid, it MUST call SyncValue/predict-ltv endpoint
   - If predicted LTV is lower than the ROI threshold set by SyncBrain, 
     the bid MUST be suppressed (MarginGuardian circuit breaker)
   - Use Kelly Criterion for risk-adjusted bid sizing

3. SyncShield Safety Gate:
   - Pass ALL cross-platform creative variants generated by SyncCreate through 
     SyncShield/risk-scan before deployment
   - If risk_score > 0.3, reject creative
   - If <2 variants approved, fall back to "Gold Standard" assets

4. Outcome-as-a-Service (OaaS) Settlement:
   - Implement a SyncLedger event emitter that records "Net Profit Uplift" 
     by comparing real-time CMS data (Shopify/WooCommerce) against historical 
     baselines from SyncValue
   - Formula: Net Profit Uplift = (New Revenue - Baseline Revenue) - 
              (New Ad Spend - Baseline Ad Spend)
   - KIKI Fee = 0.20 × Net Profit Uplift (only if positive)

5. Safe-Fail Mechanisms:
   - Automatic Rollback: If CTR drops below 80% of SyncTwin projection, 
     pause campaign and deploy Gold Standard assets
   - Circuit Breaker: If risk_score > 0.8, switch to "conservative mode" 
     and require human approval

Execution:
- Generate gRPC protobuf definitions for BidRequest, LTVRequest, RiskScanRequest
- Implement Go handler logic for MarginGuardian circuit breaker in SyncFlow
- Implement Python event emitter for Net Profit attribution in SyncLedger
- Use language choices: Go 1.24 (SyncFlow/SyncShield), Python 3.11 (SyncValue/SyncBrain)
- All inter-service calls via gRPC (not REST)

Expected Output:
- /schemas/bid_request.proto (100 lines)
- /services/syncflow/app/margin_guardian.go (200 lines)
- /services/syncvalue/app/ltv_predictor.py (150 lines)
- /services/syncledger/app/services/net_profit_calculator.py (200 lines)
```

---

## Counter-Cyclical Intelligence: Why KIKI Gets Results Naturally

The fundamental competitive advantage of KIKI Agent™ is **Counter-Cyclical Intelligence**—the ability to make decisions that native platform AIs cannot make due to their inherent conflict of interest.

### **The Problem with Native Platform AI**

**Meta Advantage+ and Google PMax are "Spend-First" Systems**:
- **Incentive Structure**: Platforms profit when you spend your entire budget, regardless of quality
- **Optimization Goal**: Maximize conversions (any transaction), not profitable customers
- **No LTV Consideration**: Will bid on low-value users just to hit daily spend targets
- **No Circuit Breaker**: No mechanism to "say no" to unprofitable bids

**Example of Native AI Waste**:
```python
# Meta Advantage+ logic (simplified)
if daily_budget_remaining > 0:
    bid_on_every_opportunity()  # Spend-first mentality
    
# Result:
# - Spends $500/day on users with $2 LTV
# - Client loses money, Meta profits from ad revenue
```

### **KIKI's "Outcome-Oriented" Natural Advantage**

**SyncValue™ + SyncShield™ = Autonomous Waste Prevention**:
1. **LTV Prediction First**: Before any bid, SyncValue predicts 12-month Lifetime Value
2. **MarginGuardian Circuit Breaker**: SyncFlow suppresses bids if `LTV / CAC < ROI_threshold`
3. **Pre-Launch Validation**: SyncTwin runs 10,000 simulations; blocks campaigns with negative Net Profit Uplift
4. **Real-Time Rollback**: If CTR drops >20%, SyncShield auto-pauses and deploys Gold Standard assets

**KIKI Natural Logic Flow**:
```python
# In SyncFlow.DecideBid()
async def decide_bid(bid_request: BidRequest) -> BidDecision:
    # Step 1: Get LTV prediction from SyncValue (not platform signal)
    ltv_prediction = await syncvalue.predict_ltv(bid_request.user_signals)
    
    # Step 2: Get ROI threshold from SyncBrain (client goal, not platform goal)
    roi_threshold = await syncbrain.get_roi_threshold(bid_request.client_id)
    
    # Step 3: MarginGuardian Circuit Breaker (KIKI's "No" button)
    expected_roi = ltv_prediction.predicted_ltv / bid_request.max_bid
    if expected_roi < roi_threshold:
        # Platform would bid here to spend budget
        # KIKI says "NO" to protect profit
        return BidDecision(
            should_bid=False,
            reason="LTV below ROI threshold - PROTECTING PROFIT"
        )
    
    # Step 4: Only bid when math proves Net Profit Uplift
    kelly_fraction = calculate_kelly_fraction(
        ltv_prediction.predicted_ltv, 
        ltv_prediction.confidence_score
    )
    optimal_bid = ltv_prediction.predicted_ltv * kelly_fraction
    
    return BidDecision(
        should_bid=True,
        bid_amount=optimal_bid,
        reason="LTV-justified bid - PROFIT EXPECTED"
    )
```

**Why This Gets Results "Naturally"**:
- ✅ **No Wasted Spend**: Only bids on high-LTV users (not just any conversion)
- ✅ **Self-Correcting**: SyncTwin validation catches unprofitable campaigns BEFORE launch
- ✅ **Platform-Independent**: Doesn't rely on Meta/Google's AI (which has conflict of interest)
- ✅ **OaaS Alignment**: KIKI only earns when client profits, so waste = $0 revenue for KIKI

**Comparison Table**:

| Decision Point | Meta Advantage+ | Google PMax | KIKI Agent™ |
|---------------|----------------|-------------|-------------|
| **Bid on low-LTV user?** | ✅ Yes (spend budget) | ✅ Yes (hit daily spend) | ❌ No (MarginGuardian blocks) |
| **Launch unprofitable campaign?** | ✅ Yes (revenue for Meta) | ✅ Yes (revenue for Google) | ❌ No (SyncTwin rejects) |
| **Continue underperforming creative?** | ✅ Yes (no rollback) | ✅ Yes (no rollback) | ❌ No (auto-pause + Gold Standard) |
| **Overspend in market shock?** | ✅ Yes (CPM spike = more Meta profit) | ✅ Yes (CPC spike = more Google profit) | ❌ No (SyncFlow shifts to cheaper platform) |

---

## Platform-Agnostic Performance: The "Universal Advertising Language"

KIKI's architecture is **Platform-Agnostic** by design. The Council of Nine speaks a "Universal Advertising Language" that translates seamlessly across Meta, Google, TikTok, LinkedIn, Amazon, and Microsoft.

### **1. Google Ads (Search & Performance Max)**

**The Problem with Google PMax**:
- **Black Box**: No transparency into where ads are placed (YouTube, Display, Search, Shopping)
- **Junk Placements**: Google will "fill" your budget with low-quality display ads if search inventory is expensive
- **Keyword Ignorance**: PMax ignores your keyword strategy and bids on broad, low-intent queries

**KIKI's Advantage**:
```python
# In SyncBrain strategy generation
async def generate_google_strategy(brand_dna: BrandDNA) -> GoogleStrategy:
    # Step 1: SyncScrape extracted brand DNA from URL
    # e.g., "Rare Beauty" → "Inclusive, Gen-Z, Mental Health Advocate"
    
    # Step 2: Generate HIGH-INTENT search keywords (not broad match)
    keywords = llm.generate_keywords(
        brand_voice=brand_dna.voice,
        intent_filter="purchase_intent_only"  # Not "awareness"
    )
    # Result: ["cruelty-free makeup", "inclusive beauty brands"]
    # NOT: ["makeup", "cosmetics"] (too broad, low LTV)
    
    # Step 3: Feed Google PMax with high-intent creative
    creative_brief = llm.generate_creative_brief(
        keywords=keywords,
        brand_dna=brand_dna,
        platform="google_pmax"
    )
    
    # Step 4: SyncCreate generates creatives optimized for Google's AI
    creatives = await synccreate.generate_creatives(
        brief=creative_brief,
        formats=["responsive_search_ads", "display_1200x627"]
    )
    
    # Step 5: SyncTwin validates: Will this get high-LTV users?
    validation = await synctwin.simulate_google_campaign(
        keywords=keywords,
        creatives=creatives,
        target_ltv_p75=brand_dna.ltv_threshold
    )
    
    if validation.confidence_score < 0.85:
        # Google would launch anyway. KIKI says "NO."
        raise CampaignRejectedError("Google PMax predicted low-LTV placements")
    
    return GoogleStrategy(
        keywords=keywords,
        creatives=creatives,
        placement_exclusions=["youtube_kids", "mobile_games"]  # Avoid junk
    )
```

**Result**: Google's AI is "guided" by KIKI's brand DNA, preventing PMax from wasting money on low-intent placements.

### **2. TikTok Ads (UGC-Style Video)**

**The Challenge**: TikTok users hate "polished ads." They want raw, authentic, user-generated content.

**KIKI's SyncCreate "Format Personality" for TikTok**:
```python
# In SyncCreate creative generation
async def generate_tiktok_creative(brand_dna: BrandDNA) -> TikTokCreative:
    # Step 1: Identify brand voice tone
    tone = "high_energy" if brand_dna.audience == "gen_z" else "conversational"
    
    # Step 2: Generate UGC-style video script
    script = llm.generate_video_script(
        brand_voice=brand_dna.voice,
        style="ugc_authentic",  # NOT "corporate"
        hook="pattern_interrupt",  # First 3 seconds critical
        length="15_seconds"  # TikTok optimal
    )
    # Example output:
    # "POV: You finally found makeup that doesn't test on animals 😭✨
    #  @RareBeauty got me like... [shows before/after]"
    
    # Step 3: Generate 9:16 vertical video (TikTok native format)
    video = await stable_diffusion.generate_video(
        script=script,
        aspect_ratio="9:16",
        style="raw_iphone_footage"  # Not studio-polished
    )
    
    # Step 4: SyncShield brand safety scan
    risk_result = await syncshield.risk_scan(
        creative_id=video.id,
        creative_type="video",
        platform="tiktok"
    )
    
    if risk_result.approved:
        return TikTokCreative(video=video, script=script)
    else:
        # Retry with adjusted tone
        return generate_tiktok_creative(brand_dna, tone="less_edgy")
```

**Result**: TikTok ads don't look like ads—they blend natively into the feed, leading to 3-5x higher CTR than "polished" corporate creatives.

### **3. LinkedIn Ads (Thought Leadership & B2B)**

**The Challenge**: LinkedIn users are in "professional mode"—they want data, whitepapers, ROI calculators.

**KIKI's SyncCreate "Format Personality" for LinkedIn**:
```python
# In SyncCreate creative generation
async def generate_linkedin_creative(brand_dna: BrandDNA) -> LinkedInCreative:
    # Step 1: Generate "Thought Leadership" angle
    thought_leadership = llm.generate_thought_leadership(
        brand_expertise=brand_dna.industry,
        target_role="VP_Marketing",  # Not "broad audience"
        content_type="data_driven"  # Stats, not fluff
    )
    # Example output:
    # "73% of B2B marketers overspend on low-LTV leads. 
    #  Here's the LTV prediction model we use at [Brand]..."
    
    # Step 2: Generate lead magnet (whitepaper, ROI calculator)
    lead_magnet = llm.generate_lead_magnet(
        topic=thought_leadership.topic,
        format="interactive_roi_calculator"  # Not static PDF
    )
    
    # Step 3: Generate LinkedIn ad creative (1200x627, professional aesthetic)
    creative = await stable_diffusion.generate_image(
        prompt=f"Professional {brand_dna.industry} infographic: {thought_leadership.headline}",
        dimensions="1200x627",
        style="corporate_clean"  # NOT "fun/playful" like TikTok
    )
    
    # Step 4: SyncShield compliance check (B2B claims must be substantiated)
    risk_result = await syncshield.risk_scan(
        creative_id=creative.id,
        creative_type="image",
        platform="linkedin",
        require_claim_substantiation=True  # LinkedIn B2B policy
    )
    
    return LinkedInCreative(
        image=creative,
        headline=thought_leadership.headline,
        lead_magnet=lead_magnet
    )
```

**Result**: LinkedIn ads position the brand as an industry expert, leading to high-quality leads (VPs, Directors) instead of low-intent clicks.

### **4. Cross-Platform Budget Fluidity: The "Holy Grail"**

**The Competitive Moat**: Real-time budget reallocation across platforms based on LTV-to-CAC ratio.

**Scenario**: Meta CPMs spike +40% on Tuesday (common during Q4 holidays).

**Traditional Approach**:
- Agency manually checks performance Friday
- By then, $5,000 wasted on overpriced Meta traffic
- Budget locked into 7-day campaigns, can't shift until next week

**KIKI's Real-Time Response**:
```go
// In SyncFlow GlobalBudgetOptimizer (runs every 5 minutes)
func (s *SyncFlowService) OptimizeBudgetAllocation(ctx context.Context) error {
    platforms := []string{"meta", "google", "tiktok", "linkedin", "amazon", "microsoft"}
    
    // Step 1: Get LTV-to-CAC ratio per platform
    platformEfficiency := make(map[string]float64)
    for _, platform := range platforms {
        ltv := s.syncValueClient.GetPlatformLTV(ctx, platform)  // From SyncValue
        cac := s.getCostPerAcquisition(ctx, platform)           // From platform API
        platformEfficiency[platform] = ltv / cac
    }
    
    // Example on Tuesday morning:
    // Meta: LTV $450 / CAC $180 = 2.5x (CPM spike)
    // TikTok: LTV $420 / CAC $105 = 4.0x (normal CPMs)
    // Google: LTV $480 / CAC $150 = 3.2x (normal)
    
    // Step 2: Detect 15% efficiency drop
    averageEfficiency := calculateAverage(platformEfficiency)
    for platform, efficiency := range platformEfficiency {
        deviation := (efficiency - averageEfficiency) / averageEfficiency
        
        if deviation < -0.15 {  // Meta is 15% below average
            log.Warn("Platform efficiency dropped",
                "platform", platform,
                "ltv_to_cac", efficiency,
                "average", averageEfficiency,
                "deviation", deviation,
            )
            
            // Step 3: Shift 20% of daily budget to best performer
            bestPlatform := findBestPlatform(platformEfficiency)  // TikTok (4.0x)
            
            currentBudget := s.getPlatformDailyBudget(ctx, platform)
            shiftAmount := currentBudget * 0.20  // $100/day
            
            s.reducePlatformBudget(ctx, platform, shiftAmount)
            s.increasePlatformBudget(ctx, bestPlatform, shiftAmount)
            
            // Step 4: Alert client via SyncNotify
            s.syncNotifyClient.SendAlert(ctx, &syncnotify.Alert{
                Severity: "INFO",
                Title:    "Budget Auto-Reallocation",
                Message:  fmt.Sprintf(
                    "Meta CPMs spiked (+40%%). Shifted $%d/day to TikTok (LTV/CAC: %.1fx vs %.1fx)",
                    int(shiftAmount), platformEfficiency[bestPlatform], efficiency,
                ),
            })
            
            // Step 5: Log to SyncLedger for OaaS attribution
            s.syncLedgerClient.RecordBudgetReallocation(ctx, platform, bestPlatform, shiftAmount)
        }
    }
    
    return nil
}
```

**Result**: 
- **Tuesday 9am**: Meta CPMs spike detected
- **Tuesday 9:05am**: $100/day shifted from Meta → TikTok (automated)
- **Tuesday 9:06am**: Client receives email: "Budget auto-reallocation saved $500 this week"
- **No human intervention required**

**Why Competitors Can't Do This**:
- **Meta Advantage+**: Meta-only (can't shift to TikTok)
- **Google PMax**: Google-only (can't shift to LinkedIn)
- **Agencies**: Manual checks (1-2 weeks reaction time)
- **KIKI**: 5-minute polling (real-time response)

---

## GitHub Copilot "Omni-Channel Sovereign" Super-Prompt

Use this prompt to build the **Universal Connector** logic that makes KIKI invincible across all platforms:

```
@workspace /agent Implement the "Omni-Channel Sovereign" logic for SyncFlow and SyncValue 
to enable real-time cross-platform budget optimization.

Objective: Create a platform-agnostic system that treats all 6 ad platforms (Meta, Google, 
TikTok, LinkedIn, Amazon, Microsoft) as a unified "Advertising Portfolio" and dynamically 
allocates capital to the highest-profit channels.

Requirements:

1. Data Normalization (Unified Performance Signal):
   - Create /schemas/performance_signal.proto with:
     - PerformanceSignal struct (platform, ltv, cac, cpm, ctr, cvr, spend, revenue)
     - Enum for Platform (META, GOOGLE, TIKTOK, LINKEDIN, AMAZON, MICROSOFT)
   - Implement /services/syncflow/app/performance_aggregator.go:
     - Fetch real-time metrics from all 6 platform APIs (Meta Insights, Google Ads API, etc.)
     - Normalize disparate schemas into unified PerformanceSignal
     - Store in Redis with 5-minute TTL (sub-millisecond lookups)

2. The Cross-Platform Pivot (GlobalBudgetOptimizer):
   - Implement /services/syncflow/app/budget_optimizer.go:
     - Calculate LTV-to-CAC ratio per platform (call SyncValue for LTV, platform APIs for CAC)
     - Detect 15% efficiency drop: if platform_efficiency < (average_efficiency - 0.15)
     - Automatic Budget Shift: Move 20% of daily budget to best-performing platform
     - Trigger: Cron job every 5 minutes (use Go cron library)
     - Alert: Send notification via SyncNotify (email/SMS/Slack)
   - Integration:
     - gRPC call to SyncValue.GetPlatformLTV(platform)
     - gRPC call to SyncLedger.RecordBudgetReallocation(from_platform, to_platform, amount)
     - gRPC call to SyncNotify.SendAlert(severity, title, message)

3. Creative Synchronicity (Cross-Platform Asset Generation):
   - Implement /services/synccreate/app/omnichannel_generator.py:
     - When SyncScrape identifies new brand USP from URL:
       - Parse brand_dna (voice, audience, values, visual_identity)
       - Trigger SyncCreate to generate platform-specific assets SIMULTANEOUSLY:
         - TikTok: 9:16 vertical video, "UGC-style" script, 15 seconds
         - LinkedIn: 1200x627 image, "Thought Leadership" whitepaper, professional tone
         - Meta: 1:1 square image, "Scroll-Stopper" hook, brand-aligned colors
         - Google: Responsive search ads (15 headlines, 4 descriptions)
     - Pass ALL variants through SyncShield.RiskScan (brand safety + compliance)
     - Deploy approved creatives to respective platforms via SyncFlow.DeployCreatives()
   - Parallel Execution: Use asyncio.gather() to generate all formats concurrently (not sequential)

4. OaaS Verification (Net Profit Uplift Aggregation):
   - Implement /services/syncledger/app/services/omnichannel_profit_calculator.py:
     - POST /webhooks/calculate-net-profit endpoint (triggered monthly, 1st of month)
     - Logic:
       - Aggregate total_revenue from CMS (Shopify/WooCommerce webhooks)
       - Aggregate total_ad_spend across ALL 6 platforms:
         - Meta: ad_spend_fetcher.get_meta_spend()
         - Google: ad_spend_fetcher.get_google_spend()
         - TikTok: ad_spend_fetcher.get_tiktok_spend()
         - LinkedIn: ad_spend_fetcher.get_linkedin_spend()
         - Amazon: ad_spend_fetcher.get_amazon_spend()
         - Microsoft: ad_spend_fetcher.get_microsoft_spend()
       - Get baseline_revenue and baseline_ad_spend from SyncValue (90-day historical avg)
       - Calculate: net_profit_uplift = (total_revenue - baseline_revenue) - (total_ad_spend - baseline_ad_spend)
       - Calculate: kiki_fee = net_profit_uplift * 0.20 if net_profit_uplift > 0 else 0.00
     - Store in PostgreSQL ledger_entries table with platform-by-platform breakdown
     - Trigger SyncBill.GenerateInvoice(kiki_fee, platform_breakdown)

5. Safe-Fail Mechanisms (Automatic Rollback Across Platforms):
   - Implement /services/syncshield/app/omnichannel_performance_monitor.go:
     - Monitor ALL platforms simultaneously (parallel goroutines, one per platform)
     - For each platform:
       - Get baseline metrics from SyncTwin.GetProjection(campaign_id)
       - Get real-time metrics from platform API
       - Calculate deviation: (real_metric - baseline_metric) / baseline_metric
       - If CTR deviation < -0.20 (20% drop):
         - Pause campaign on that platform
         - Deploy Gold Standard assets to that platform
         - Alert client: "Auto-rollback on [Platform]"
       - If risk_score > 0.8 (aggregate across all metrics):
         - Switch platform to CONSERVATIVE mode (50% budget cap)
         - Require human approval for next iteration
     - Log all rollback events to SyncLedger for OaaS attribution

Execution:
- Generate gRPC protobuf definitions for PerformanceSignal
- Implement Go services: performance_aggregator.go, budget_optimizer.go, omnichannel_performance_monitor.go
- Implement Python services: omnichannel_generator.py, omnichannel_profit_calculator.py
- Use language choices: Go 1.24 (SyncFlow/SyncShield), Python 3.11 (SyncCreate/SyncLedger)
- All inter-service calls via gRPC (not REST)
- Use asyncio for concurrent creative generation
- Use goroutines for concurrent platform monitoring

Expected Output:
- /schemas/performance_signal.proto (80 lines)
- /services/syncflow/app/performance_aggregator.go (250 lines)
- /services/syncflow/app/budget_optimizer.go (300 lines)
- /services/synccreate/app/omnichannel_generator.py (400 lines)
- /services/syncledger/app/services/omnichannel_profit_calculator.py (250 lines)
- /services/syncshield/app/omnichannel_performance_monitor.go (350 lines)

Success Metrics (30 days post-deployment):
- Cross-platform budget shifts: 15-25 per month (automated response to market shocks)
- Platform efficiency variance: <10% (balanced allocation)
- Net Profit Uplift accuracy: >98% (multi-platform attribution)
- Creative deployment time: <2 hours (URL → 5 platforms live)
```

---

## The Antler Investor Hook: "Dynamic Asset Allocator"

**When partners ask**: _"What if Meta changes their algorithm?"_

**Your answer**:
> _"KIKI doesn't care. We don't rely on one platform's AI. Our **SyncTwin™** simulates the algorithm shock in 10,000 scenarios, **SyncShield™** pauses the at-risk campaigns within 5 minutes, and **SyncFlow™** moves the capital to wherever the profit is highest—whether that's Google Search, TikTok, or LinkedIn. We aren't an 'Ad-Tech' tool optimizing for clicks. We're a **Dynamic Asset Allocator** for marketing capital, treating your ad budget like a hedge fund treats financial assets: **shift to the highest risk-adjusted return in real-time**."_

**Why This Wins**:
- ✅ **Reframes KIKI**: Not "another AI marketing tool," but "Capital Allocation Intelligence"
- ✅ **De-Risks Platform Dependency**: Meta/Google algorithm changes become irrelevant
- ✅ **Demonstrates Sophistication**: "Hedge fund for marketing" resonates with investors
- ✅ **Aligns with OaaS**: Only earn when allocation decisions create profit

**Follow-Up Visual**: _"Would you like to see the Cross-Platform Revenue Dashboard? It shows the money moving between platforms in real-time to chase the highest profit."_

---

## Infrastructure
- All services have Dockerfiles and are orchestrated via docker-compose and Kubernetes manifests in `/deploy`.
- API Gateway (Python FastAPI, placeholder for Kong/Traefik) proxies requests to services.
- Service mesh (Istio/Linkerd) and gRPC for internal agent communication.
- PostgreSQL, Redis, MinIO/S3 for data/model storage.

## Developer Workflows
- **Build/Run**: Use `docker-compose up` for local dev. For Kubernetes, apply manifests in `/deploy`.
- **Testing**: Each service has a `/tests` folder with unit/integration tests. Use pytest (Python), Go test, or Jest as appropriate.
- **API**: All APIs are RESTful, with OpenAPI schemas where possible. See `/openapi/openapi.yaml` and `/docs/API_REFERENCE.md`.
- **CI/CD**: GitHub Actions workflows and Terraform scripts are in `/deploy`.

## Conventions
- Strong typing (Python typing, Go structs, TypeScript).
- Docstrings and comments required for all modules and functions.
- Health checks at `/healthz` for all services.
- Use `/shared`, `/schemas`, `/utils`, `/types`, `/constants` for cross-service code and definitions.
- All external service calls should be mocked in tests.

## Examples
- See `/services/syncbrain/app/main.py` for FastAPI patterns and context management.
- See `/services/syncvalue/app/ltv_dRNN.py` for model structure.
- See `/services/syncflow/app/main.go` for high-performance Go API.

## Integration Points
- Internal service calls use gRPC or REST via the service mesh.
- API Gateway aggregates and authenticates all external traffic.
- Adapters for Meta/Google APIs are in SyncFlow.
- CRM integrations are in SyncEngage.

## Monitoring & Compliance
- Prometheus/Grafana for monitoring (add exporters as needed).
- SyncShield logs all compliance/audit events.

## Execution Plan for Copilot Agent Mode

When implementing KIKI Agent™ features, follow this incremental approach:

### **Phase 1: Foundation (Start Here)**
1. **Generate gRPC Protocol Buffers** for service contracts:
   ```protobuf
   // Example: /schemas/ledger_service.proto
   service LedgerService {
     rpc RecordTransaction(TransactionRequest) returns (TransactionResponse);
     rpc GetNetProfitUplift(UpliftRequest) returns (UpliftResponse);
   }
   ```
2. **Initialize SyncLedger** database schema:
   - Create PostgreSQL migrations for `stores`, `baseline_snapshots`, `ledger_entries` tables
   - See `/services/syncledger/migrations/2026_02_07_001_add_multi_platform_support.sql` for reference

### **Phase 2: OaaS Intake Portal**
3. **Build Next.js 14 ROI Calculator**:
   - Location: `/services/syncportal/app/(marketing)/roi-calculator/page.tsx`
   - Components: `HeroSection.tsx`, `ROICalculator.tsx`, `ComparisonTable.tsx`
   - Dark-mode aesthetic with Tailwind CSS + Framer Motion animations
4. **Client Dashboard**:
   - Real-time Net Profit Uplift charts (recharts/D3.js)
   - Platform-by-platform spend breakdown
   - Historical baseline vs. new revenue visualization

### **Phase 3: SyncTwin Gatekeeper Implementation**
5. **Pre-Launch Validation Hook**:
   - Location: `/services/synctwin/app/gatekeeper.py`
   - **Integration**: Add hook to `SyncBrain.GenerateStrategy()` method
   - **Logic**:
     ```python
     # In SyncBrain before returning strategy:
     twin_result = await synctwin_client.SimulateStrategy(strategy_json)
     if twin_result.confidence_score < 0.85:
         raise CampaignRejectedError(
             f"SyncTwin rejected: Projected Net Profit Uplift is negative. "
             f"ConfidenceScore: {twin_result.confidence_score}"
         )
     ```
   - **Output**: Returns `ConfidenceScore`, `RiskProfile`, `ProjectedNetProfitUplift`
6. **Chaos Testing Cron Job**:
   - Location: `/services/synctwin/app/chaos_scheduler.py`
   - **Trigger**: Runs every midnight (cron: `0 0 * * *`)
   - **Test Scenarios**:
     - Simulate +50% Meta CPMs (sudden market shock)
     - Simulate -30% conversion rate drop
     - Simulate ad platform API outage (timeout errors)
   - **Validation**: Verify MarginGuardian circuit breaker triggers in SyncFlow
   - **Alert**: Send to SyncNotify if any test fails
7. **Real-to-Sim Synchronization**:
   - Location: `/services/synctwin/app/mirror_sync.py`
   - **gRPC Stream**: Subscribe to `SyncFlow.BidStream` for real-time updates
   - **Logic**:
     ```python
     async for bid_event in syncflow.stream_bids():
         mirror_state.update(bid_event)
         deviation = abs(real_performance - twin_projection) / twin_projection
         if deviation > 0.15:  # >15% deviation
             await syncflow.trigger_rollback(campaign_id)
             await syncnotify.alert("Auto-Rollback", f"Deviation: {deviation:.1%}")
     ```
   - **Storage**: Use Redis for sub-millisecond state updates

### **Phase 4: SyncScrape Implementation**
8. **URL-to-Campaign Engine**:
   - Create `/services/syncscrape/app/scraper.py` (Playwright)
   - Implement visual identity extraction (colors, fonts, logo)
   - Implement brand voice extraction (GPT-4 summarization)
9. **Integration Pipeline**:
   - Call SyncCreate for ad creative generation
   - Call SyncBrain for ad copy variations
   - Call SyncFlow to deploy campaigns

### **Phase 5: CMS Integration**
10. **OAuth Connectors**:
   - Shopify: `/services/syncengage/integrations/shopify.py`
   - WooCommerce: `/services/syncengage/integrations/woocommerce.py`
11. **Revenue Data Pipeline**:
   - Webhook listeners for `order.created`, `order.updated`
   - Feed transaction data to SyncValue for LTV updates

### **Phase 6: Financial Settlement**
12. **SyncLedger Net Profit Calculation**:
   - Use `/services/syncledger/app/services/ad_spend_fetcher_extended.py` (already implemented)
   - Implement daily baseline updates from SyncValue
13. **SyncBill Automated Invoicing**:
    - Stripe integration for payment processing
    - PDF invoice generation with detailed breakdown
    - Email delivery via SendGrid

### **Incremental Testing Strategy**
- After each phase, run integration tests in `/tests` folder
- Use `docker-compose up <service>` to test individual services
- Verify gRPC communication with BloomRPC or grpcurl

### **How to Use This with Copilot**
1. **Context First**: Open relevant files in workspace (e.g., `ARCHITECTURE.md`, existing service files)
2. **Agent Mode**: Use `@workspace /agent` to create multiple files at once
3. **Iterative**: If output too long, say: "Focus only on [specific component] for now"
4. **Examples**: Reference existing patterns:
   - FastAPI: See `/services/syncbrain/app/main.py`
   - Go API: See `/services/syncflow/app/main.go`
   - gRPC: See `/shared/proto/*.proto`

### **Example Prompts for SyncTwin Implementation**

**Prompt 1: Pre-Launch Validation (Digital Handshake)**
```
@workspace /agent Implement the SyncTwin 'Simulation Gatekeeper' logic.

Add a hook to SyncBrain.GenerateStrategy() in /services/syncbrain/app/main.py. 
Before returning the final strategy JSON, it must call SyncTwin.SimulateStrategy() 
via gRPC and only proceed if the ConfidenceScore > 0.85.

If the simulation predicts negative Net Profit Uplift, raise CampaignRejectedError 
and log to SyncShield audit trail with reason code "SYNCTWIN_NEGATIVE_FORECAST".

Return: ConfidenceScore, RiskProfile, ProjectedNetProfitUplift
```

**Prompt 2: Chaos Testing Automation**
```
@workspace /agent Create a cron-job service at /services/synctwin/app/chaos_scheduler.py 
that triggers SyncTwin.RunChaosTest every midnight (cron: 0 0 * * *).

Test scenarios:
1. Simulate +50% Meta CPM increase (market shock)
2. Simulate -30% conversion rate drop
3. Simulate ad platform API outage (5-minute timeout)

Verify that SyncFlow's MarginGuardian circuit breaker triggers correctly.
If any test fails, send alert to SyncNotify with severity: CRITICAL.

Use Ray for distributed simulation across 10,000 concurrent scenarios.
```

**Prompt 3: Real-Time Synchronization**
```
@workspace /agent Implement Real-to-Sim synchronization in /services/synctwin/app/mirror_sync.py.

Subscribe to SyncFlow.BidStream gRPC stream for real-time bidding events.
Maintain a parallel "digital twin" state in Redis with sub-millisecond latency.

Logic:
- For each bid event, update mirror state
- Calculate deviation: |real_performance - twin_projection| / twin_projection
- If deviation > 15%, trigger auto-rollback in SyncFlow via gRPC
- Send SyncNotify alert: "Auto-Rollback triggered - {deviation:.1%} deviation"

Use asyncio for concurrent stream processing.
```

**Why This Matters for OaaS**:
SyncTwin's autonomous triggers protect your 20% success fee by preventing unprofitable campaigns 
from launching. This "Digital Insurance" is a massive competitive advantage:
- **Before KIKI**: Agencies charge flat fees, no performance guarantees
- **With KIKI**: Only pay when you profit (20% of Net Profit Uplift)
- **SyncTwin's Role**: Blocks campaigns predicted to lose money BEFORE launch

---
For more details, see `/docs/ARCHITECTURE.md` and `/docs/AGENT_SPEC.md`.
