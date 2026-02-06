# KIKI Agent™ - Campaign Automation

## Overview

**Council of Nine** is KIKI Agent's flagship orchestration feature that transforms user input into a complete, deployed advertising campaign. This implements KIKI's "Advantage+ Suite" - Meta's automation features enhanced with LTV prediction, autonomous creative generation, and brand safety compliance.

## Two Entry Points

Users can interact with KIKI through **two primary entry points**:

### ⭐ 1. Prompt-to-Campaign (PRIMARY)

Transform natural language prompts into campaigns - **no website required**.

**Example Prompts**:
- "Launch product with $100k budget, target ROI 3x"
- "Create campaign for SaaS startup, B2B enterprise audience"
- "Mobile game launch, casual players, $50k budget, ROI 2.5x"

**How it works**:
1. **SyncBrain™** parses the prompt → Extracts budget, ROI, industry, audience, brand intent
2. **SyncValue™** predicts LTV baseline → Calculates max CPA from ROI target (e.g., ROI 3x → max CPA = LTV/3)
3. **SyncBrain™** generates campaign strategy based on parsed intent
4. **SyncCreate™** generates 5 ad copies + 3 image prompts
5. **SyncShield™** validates all assets for brand safety and compliance
6. **SyncFlow™** deploys campaign with budget & ROI constraints (if auto_deploy=true)

**Use Case**: Perfect for testing new product concepts, quick campaign launches, or when you don't have an existing website yet.

---

### 2. URL-to-Campaign

Transform an existing website into a campaign by extracting brand identity.

**Example**:
- Input: `https://shopify.com`
- Output: Complete campaign with on-brand creative, LTV prediction, and deployment

**How it works**:
1. **SyncValue™** scrapes URL → Extracts brand identity (name, colors, tone, values)
2. **SyncValue™** classifies industry → E-commerce, SaaS, Gaming, etc.
3. **SyncValue™** predicts LTV baseline → $60-$2,500+ depending on industry
4. **SyncBrain™** generates campaign strategy based on brand and industry
5. **SyncCreate™** generates on-brand ad copies and image prompts
6. **SyncShield™** validates brand safety
7. **SyncFlow™** deploys with LTV constraints (if auto_deploy=true)

**Use Case**: Perfect for existing businesses with established websites and brand identities.

---

## The Advantage+ Suite

KIKI enhances Meta's core automation features:

### 1. Advantage+ Audience → **SyncValue™ + SyncBrain™**

**Meta's Feature**: Finds audiences beyond initial targeting to lower costs

**KIKI's Enhancement**: 
- **SyncValue™** predicts the actual long-term value (LTV) of discovered audiences
- **SyncBrain™** orchestrates targeting strategies based on which "unconventional" audiences have the highest predicted retention
- **Result**: LTV-based targeting instead of just cost-per-acquisition optimization

**Agents Involved**: SyncValue, SyncBrain

### 2. Advantage+ Creative → **SyncCreate™ + SyncShield™**

**Meta's Feature**: Automatically swaps existing creative assets to improve performance

**KIKI's Enhancement**:
- **SyncCreate™** generates new on-brand creatives autonomously using Stable Diffusion
- **SyncShield™** ensures every generated version meets enterprise brand safety and compliance standards
- **Result**: Autonomous creative generation, not just asset swapping

**Agents Involved**: SyncCreate, SyncShield

### 3. Advantage+ Placements → **SyncFlow™**

**Meta's Feature**: Automatically finds cheapest placements across networks

**KIKI's Enhancement**:
- **SyncFlow™** handles sub-millisecond bidding execution across networks
- Doesn't just find the "cheapest" placement—finds the placement most likely to convert a **high-LTV customer**
- **Result**: LTV-optimized placement selection with <1ms real-time bidding

**Agents Involved**: SyncFlow

---

## URL-to-Insight: Industry Discovery

When a user inputs a URL, KIKI automatically:

1. **Scrapes the website** to identify:
   - Brand identity (colors, tone, products)
   - Product catalog and pricing
   - Business model indicators
   - Content keywords and meta information

2. **Classifies the industry** using heuristic-based analysis:
   - **E-commerce & Retail**
   - **SaaS & Software** (B2B or B2C)
   - **Mobile Gaming & Apps**
   - **Professional Services**
   - **Education & E-Learning**
   - **Health & Wellness**
   - **Financial Services**

3. **Determines optimal campaign strategy**:
   - **ASC (Advantage+ Shopping Campaigns)**: For e-commerce, retail, mobile apps
   - **ALC (Advantage+ Lead Campaigns)**: For SaaS, services, B2B

4. **Predicts LTV baseline** based on industry benchmarks:
   - E-commerce: $60-250 depending on product category
   - SaaS B2B: $2,500+ for enterprise
   - SaaS B2C: $150+ for consumer
   - Mobile Gaming: $25-100 (volume play with whale targeting)
   - Professional Services: $1,500+ (high-ticket)

---

## Orchestration Flow

The Council of Nine coordinates all KIKI agents in a 6-phase workflow:

### Phase 1: Discovery & Analysis (SyncValue)
- Scrape URL using Playwright + BeautifulSoup
- Extract brand identity (colors, tone, products, keywords)
- Classify industry category and subcategory
- Determine business model (B2C, B2B, B2B2C)
- Predict LTV baseline for industry

**Output**: BrandIdentity + IndustryProfile

### Phase 2: Strategic Planning (SyncBrain)
- Generate campaign strategy using LLM orchestration
- Define target audience based on industry and brand
- Create key messaging and tone guidance
- Output visual guidelines for creative generation

**Output**: CampaignBrief

### Phase 3: Creative Generation (SyncCreate)
- Generate **5 ad copy variations** using campaign brief
- Generate **3 image prompts** for Stable Diffusion
- All creatives are brand-aligned and industry-appropriate

**Output**: 5 ad copies + 3 image prompts

### Phase 4: Brand Safety & Compliance (SyncShield)
- Validate all ad copies for brand safety
- Check sentiment alignment with brand identity
- Ensure compliance with enterprise standards
- Flag any concerns for manual review

**Output**: Safety validation + Compliance status

### Phase 5: Campaign Deployment (SyncFlow) - Optional
- Deploy campaign to real-time bidding engine
- Apply LTV-based bidding constraints
- Configure placement optimization for high-LTV audiences
- Monitor performance in real-time

**Output**: Deployment ID + Campaign status

### Phase 6: Audit Logging (SyncShield)
- Log complete campaign deployment for audit trail
- Track all generated assets and safety validations
- Enable compliance reporting and forensics

---

## Optimal Industries for KIKI

Based on the 12-agent architecture, KIKI is best suited for industries where **retention** and **LTV** drive profit:

### 1. E-commerce & Retail
**Why**: SyncCreate handles high-volume creative refreshes, SyncEngage manages post-purchase loyalty

**Campaign Type**: ASC (Advantage+ Shopping Campaigns)

**LTV Baseline**: $60-250

**Subcategories**:
- Fast Fashion: $60 LTV, mid price point
- Luxury Goods: $250 LTV, premium price point
- Consumer Electronics: $150 LTV, high price point

### 2. Subscription SaaS
**Why**: SyncValue identifies at-risk users early to trigger SyncShield-protected retention offers

**Campaign Type**: ALC (Advantage+ Lead Campaigns)

**LTV Baseline**: $150-2,500

**Subcategories**:
- Enterprise B2B: $2,500 LTV, premium pricing
- Consumer SaaS: $150 LTV, mid pricing

### 3. Mobile Gaming & Apps
**Why**: SyncFlow bids aggressively for "whales" (high-spenders) based on first-session behavior predictions

**Campaign Type**: ASC (App Install)

**LTV Baseline**: $25-100

**Subcategories**:
- Casino & Gambling: $100 LTV (whales drive revenue)
- Casual Gaming: $25 LTV (volume play)

---

## API Usage

### Endpoint: `POST /api/v1/prompt-to-campaign` (⭐ PRIMARY)

Transform a natural language prompt into a complete advertising campaign.

**Request**:
```json
{
  "prompt": "Launch product with $100k budget, target ROI 3x",
  "auto_deploy": false
}
```

**Response**:
```json
{
  "success": true,
  "deployment": {
    "deployment_id": "prompt_campaign_xyz789",
    "url": null,
    "brand_name": "New Product Launch",
    "industry_category": "General",
    "campaign_type": "ASC",
    "ltv_baseline": 100.0,
    "budget": 100000.0,
    "target_roi": 3.0,
    "max_cpa": 33.33,
    "ad_copies": [
      "Discover New Product Launch - Transform your experience",
      "New Product Launch: Quality you can trust",
      "Join thousands who love New Product Launch",
      "Experience the New Product Launch difference today",
      "Limited time offer: Get started with New Product Launch"
    ],
    "image_prompts": [
      "Professional product shot, clean background, studio lighting",
      "Lifestyle image, happy customers, modern aesthetic",
      "Abstract brand identity, vibrant colors, minimalist design"
    ],
    "brand_safe": true,
    "compliance_status": "approved",
    "deployment_status": "draft",
    "created_at": "2026-02-06T10:00:00Z"
  },
  "financial_summary": {
    "budget": 100000.0,
    "target_roi": 3.0,
    "ltv_baseline": 100.0,
    "max_cpa": 33.33,
    "roi_calculation": "LTV $100.00 / Target ROI 3.0x = Max CPA $33.33"
  },
  "next_steps": [
    "Review generated ad copies and image prompts",
    "Verify budget and ROI constraints",
    "Deploy to SyncFlow when ready (if not auto-deployed)",
    "Monitor performance via SyncPortal dashboard"
  ]
}
```

### Parameters

- **`prompt`** (required): Natural language campaign description
- **`auto_deploy`** (optional, default: false): Automatically deploy to SyncFlow if brand safety passes

### Example Prompts

```bash
# Budget + ROI constraint
curl -X POST http://localhost:8002/api/v1/prompt-to-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Launch product with $100k budget, target ROI 3x"
  }'

# Industry + audience targeting
curl -X POST http://localhost:8002/api/v1/prompt-to-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create campaign for SaaS startup, B2B enterprise audience, $50k budget"
  }'

# Mobile game campaign
curl -X POST http://localhost:8002/api/v1/prompt-to-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Mobile game launch, casual players, $25k budget, ROI 2.5x"
  }'

# E-commerce with demographics
curl -X POST http://localhost:8002/api/v1/prompt-to-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "E-commerce store for organic skincare, target millennials, $40k budget",
    "auto_deploy": true
  }'
```

### Prompt Parsing

**SyncBrain™** extracts structured data from natural language:

| Extracted Field | Example Values | Prompt Keywords |
|----------------|----------------|-----------------|
| **Budget** | $25,000 - $1,000,000 | "$100k", "$25k budget" |
| **Target ROI** | 2.0x - 5.0x | "ROI 3x", "target ROI 2.5x" |
| **Industry** | E-commerce, SaaS, Gaming, etc. | "saas", "mobile game", "ecommerce" |
| **Audience** | B2B, B2C, demographics | "enterprise", "millennials", "casual players" |
| **Business Model** | B2B, B2C, Freemium | "b2b", "subscription", "freemium" |

### ROI Calculation

When a target ROI is specified, KIKI automatically calculates max CPA:

```
Max CPA = LTV Baseline / Target ROI

Example:
- LTV Baseline: $100
- Target ROI: 3x
- Max CPA: $100 / 3 = $33.33
```

**SyncFlow™** enforces this constraint in real-time bidding to ensure campaigns never exceed the specified ROI target.

---

### Endpoint: `POST /api/v1/url-to-campaign`

**Request**:
```json
{
  "url": "https://example.com",
  "auto_deploy": false
}
```

**Response**:
```json
{
  "success": true,
  "deployment": {
    "deployment_id": "campaign_abc123xyz",
    "url": "https://example.com",
    "brand_name": "Example Corp",
    "industry_category": "E-commerce & Retail",
    "campaign_type": "ASC",
    "ltv_baseline": 75.0,
    "ad_copies": [
      "Discover Example Corp - Transform your shopping experience",
      "Example Corp: Quality you can trust",
      "Join thousands who love Example Corp",
      "Experience the Example Corp difference today",
      "Shop Example Corp - Limited time offer"
    ],
    "image_prompts": [
      "Professional product shot of Example Corp products, clean background",
      "Example Corp lifestyle image, happy customers, modern aesthetic",
      "Abstract brand identity for Example Corp, vibrant colors"
    ],
    "brand_safe": true,
    "compliance_status": "approved",
    "deployment_status": "draft",
    "created_at": "2026-02-06T10:00:00Z"
  },
  "next_steps": [
    "Review generated ad copies and image prompts",
    "Deploy to SyncFlow when ready",
    "Monitor performance via SyncPortal dashboard"
  ]
}
```

### Parameters

- **`url`** (required): Target business website URL
- **`auto_deploy`** (optional, default: false): Automatically deploy to SyncFlow if brand safety passes

### With Auto-Deploy

```bash
curl -X POST http://localhost:8002/api/v1/url-to-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://shopify.com",
    "auto_deploy": true
  }'
```

If `auto_deploy=true` and brand safety passes:
- Campaign is automatically deployed to SyncFlow
- `syncflow_deployment_id` is populated
- `deployment_status` becomes `"deployed"`
- `deployed_at` timestamp is set

---

## Industry Classification Examples

### E-commerce Example
**URL**: `https://www.nike.com`

**Classification**:
- Category: E-commerce & Retail
- Subcategory: Fast Fashion
- Business Model: B2C
- Price Point: mid
- Campaign Type: ASC
- LTV Baseline: $60
- Confidence: 0.8

### SaaS Example
**URL**: `https://www.salesforce.com`

**Classification**:
- Category: SaaS & Software
- Subcategory: Enterprise B2B
- Business Model: B2B
- Price Point: premium
- Campaign Type: ALC
- LTV Baseline: $2,500
- Confidence: 0.85

### Mobile App Example
**URL**: `https://www.duolingo.com`

**Classification**:
- Category: Education & E-Learning
- Subcategory: Mobile App
- Business Model: B2C
- Price Point: mid
- Campaign Type: ALC
- LTV Baseline: $300
- Confidence: 0.8

---

## Example Usage

### Python

```python
import asyncio
import httpx

async def create_campaign(url: str):
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "http://localhost:8002/api/v1/url-to-campaign",
            json={"url": url, "auto_deploy": False}
        )
        
        if response.status_code == 200:
            result = response.json()
            deployment = result["deployment"]
            
            print(f"✅ Campaign created for {deployment['brand_name']}")
            print(f"Industry: {deployment['industry_category']}")
            print(f"LTV Baseline: ${deployment['ltv_baseline']:.2f}")
            print(f"\nGenerated {len(deployment['ad_copies'])} ad copies:")
            for copy in deployment['ad_copies']:
                print(f"  • {copy}")
            
            return deployment

# Run
asyncio.run(create_campaign("https://shopify.com"))
```

### cURL

```bash
# Draft mode (no auto-deploy)
curl -X POST http://localhost:8002/api/v1/url-to-campaign \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Auto-deploy mode
curl -X POST http://localhost:8002/api/v1/url-to-campaign \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "auto_deploy": true}'
```

---

## Quick Start

1. **Ensure services are running**:
   ```bash
   docker-compose up syncvalue syncbrain synccreate syncshield syncflow
   ```

2. **Run the example script**:
   ```bash
   python services/syncvalue/example_url_to_campaign.py
   ```

3. **Or use the API directly**:
   ```bash
   curl -X POST http://localhost:8002/api/v1/url-to-campaign \
     -H "Content-Type: application/json" \
     -d '{"url": "https://nike.com"}'
   ```

---

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                     Council of Nine                             │
│                   (Orchestration Layer)                          │
└────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  SyncValue™  │      │  SyncBrain™  │      │ SyncCreate™  │
│              │      │              │      │              │
│ • Scraping   │──────│ • Strategy   │──────│ • Ad Copies  │
│ • Industry   │      │ • Targeting  │      │ • Image Gen  │
│ • LTV        │      │ • Messaging  │      │ • Stable AI  │
└──────────────┘      └──────────────┘      └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ SyncShield™  │      │  SyncFlow™   │      │ SyncEngage™  │
│              │      │              │      │              │
│ • Safety     │      │ • Bidding    │      │ • Retention  │
│ • Compliance │      │ • Deployment │      │ • Triggers   │
│ • Audit Log  │      │ • <1ms RTB   │      │ • Churn      │
└──────────────┘      └──────────────┘      └──────────────┘
```

---

## Next Steps

1. **Review generated campaigns**: Check ad copies and image prompts for brand alignment
2. **Customize as needed**: Edit any assets before deployment
3. **Deploy to SyncFlow**: Use auto_deploy or manually deploy via SyncFlow API
4. **Monitor performance**: Track via SyncPortal dashboard
5. **Iterate**: Use performance data to refine targeting and creative

---

## Related Documentation

- [SyncValue README](../syncvalue/README.md) - LTV prediction and scraper module
- [Council of Nine Source](../syncvalue/council_of_nine.py) - Orchestrator implementation
- [API Reference](../../docs/API_REFERENCE.md) - Complete API documentation
- [Architecture](../../docs/ARCHITECTURE.md) - System architecture overview

---

**Status**: ✅ Production-ready  
**Last Updated**: February 6, 2026  
**Developer**: GitHub Copilot  
**License**: Part of KIKI Agent™ platform
