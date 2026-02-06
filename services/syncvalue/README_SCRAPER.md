# SyncScrape Module

## Overview

**SyncScrape** is an intelligent brand identity extraction and campaign asset generation module within the KIKI Agent™ platform. It automates the process of:

1. **Extracting brand identity** from websites (colors, tone, products)
2. **Generating campaign briefs** using AI (SyncBrain)
3. **Creating marketing assets** (ad copies & image prompts via SyncCreate)
4. **Validating brand safety** and compliance (SyncShield)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SyncScrape Workflow                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Data Extraction (Playwright + BeautifulSoup)            │
│     └─> BrandIdentityExtractor                              │
│         • Colors, Tone, Products, Keywords                  │
│                                                              │
│  2. Context Enrichment (SyncBrain)                          │
│     └─> SyncBrainClient                                     │
│         • LLM-generated CampaignBrief                       │
│                                                              │
│  3. Asset Generation (SyncCreate)                           │
│     └─> SyncCreateClient                                    │
│         • 5 ad copy variations                              │
│         • 3 image prompts                                   │
│                                                              │
│  4. Safety Check (SyncShield)                               │
│     └─> SyncShieldClient                                    │
│         • Brand safety validation                           │
│         • Sentiment alignment                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Domain Models

- **BrandIdentity**: Extracted brand information (colors, tone, products, keywords)
- **CampaignBrief**: AI-generated campaign strategy and guidelines
- **GeneratedAsset**: Creative asset (ad copy or image prompt) with validation status

### Service Clients

- **SyncBrainClient**: Integrates with SyncBrain for LLM-based campaign planning
- **SyncCreateClient**: Integrates with SyncCreate for creative generation
- **SyncShieldClient**: Integrates with SyncShield for compliance validation

### Orchestrator

- **SyncScrapeOrchestrator**: Coordinates the entire workflow end-to-end

## Installation

### 1. Install Python Dependencies

```bash
cd /services/syncvalue
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

```bash
playwright install chromium
```

## Usage

### Command Line

```bash
# Basic usage
python scraper.py https://example.com

# The script will:
# 1. Extract brand identity
# 2. Generate campaign brief
# 3. Create 5 ad copies and 3 image prompts
# 4. Validate all assets for brand safety
```

### Programmatic Usage

```python
from scraper import SyncScrapeOrchestrator

async def run_scrape():
    orchestrator = SyncScrapeOrchestrator()
    
    result = await orchestrator.execute(
        url="https://example.com",
        campaign_goal="brand awareness",
        num_ad_copies=5,
        num_image_prompts=3
    )
    
    print(f"Brand: {result['brand_identity']['brand_name']}")
    print(f"Generated {len(result['generated_assets']['copies'])} ad copies")
    print(f"Approval rate: {result['metrics']['approval_rate']}%")

# Run
import asyncio
asyncio.run(run_scrape())
```

### API Integration (FastAPI)

Add to your FastAPI service:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from scraper import SyncScrapeOrchestrator

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: HttpUrl
    campaign_goal: str = "brand awareness"
    num_ad_copies: int = 5
    num_image_prompts: int = 3

@app.post("/scrape-and-generate")
async def scrape_and_generate(req: ScrapeRequest):
    """Extract brand identity and generate campaign assets"""
    orchestrator = SyncScrapeOrchestrator()
    
    try:
        result = await orchestrator.execute(
            url=str(req.url),
            campaign_goal=req.campaign_goal,
            num_ad_copies=req.num_ad_copies,
            num_image_prompts=req.num_image_prompts
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Output Format

```json
{
  "status": "success",
  "brand_identity": {
    "url": "https://example.com",
    "brand_name": "Example Corp",
    "primary_colors": ["#FF5733", "#33FF57"],
    "secondary_colors": ["#3357FF"],
    "tone": "professional",
    "product_catalog": [
      {"name": "Product A", "price": "$99.99", "image_url": "..."}
    ],
    "meta_description": "Leading solutions provider",
    "keywords": ["innovation", "quality", "service"],
    "logo_url": "https://example.com/logo.png"
  },
  "campaign_brief": {
    "campaign_id": "campaign_1738857600.123",
    "target_audience": "Tech professionals",
    "key_message": "Innovative solutions for modern businesses",
    "tone_guidance": "professional",
    "visual_guidelines": {
      "colors": ["#FF5733", "#33FF57"],
      "logo": "https://example.com/logo.png",
      "style": "professional"
    }
  },
  "generated_assets": {
    "copies": [
      {
        "asset_id": "copy_0",
        "content": "Discover innovative solutions...",
        "brand_safe": true,
        "sentiment_score": 0.85,
        "compliance_status": "approved"
      }
    ],
    "image_prompts": [
      {
        "asset_id": "img_prompt_0",
        "content": "A professional image featuring...",
        "brand_safe": true,
        "sentiment_score": 0.75,
        "compliance_status": "approved"
      }
    ]
  },
  "metrics": {
    "total_assets": 8,
    "approved_assets": 7,
    "approval_rate": 87.5,
    "extracted_products": 3,
    "extracted_colors": 5
  }
}
```

## Testing

```bash
# Run all tests
pytest tests/test_scraper.py -v

# Run with coverage
pytest tests/test_scraper.py --cov=scraper --cov-report=html

# Run performance tests
pytest tests/test_scraper.py -v -m performance
```

## Configuration

Configure service URLs via environment variables or `shared/config.py`:

```python
SYNCBRAIN_URL = "http://syncbrain:8001"
SYNCCREATE_URL = "http://synccreate:8004"
SYNCSHIELD_URL = "http://syncshield:8006"
```

## Features

### Data Extraction

- **Playwright**: Renders JavaScript, extracts dynamic content, captures CSS colors
- **BeautifulSoup**: Parses HTML structure for products, keywords, meta tags
- **Smart Extraction**:
  - Brand name from og:site_name, title, or h1
  - Color palette from computed CSS styles
  - Tone inference from content analysis
  - Product catalog from e-commerce patterns
  - SEO metadata and keywords

### Context Enrichment

- Sends extracted brand identity to **SyncBrain**
- Receives LLM-generated **CampaignBrief** with:
  - Target audience analysis
  - Key messaging strategy
  - Tone and visual guidelines

### Asset Generation

- Triggers **SyncCreate** to generate:
  - **5 ad copy variations** (customizable)
  - **3 image prompts** (customizable)
- Each asset tailored to campaign brief and brand identity

### Safety Validation

- **SyncShield** validates each asset for:
  - Brand safety (negative keyword detection)
  - Sentiment alignment (positive/negative scoring)
  - Brand keyword alignment
  - Compliance status (approved/rejected)

## Error Handling

- Network errors: Retries with exponential backoff (via httpx)
- Extraction failures: Graceful degradation (partial data)
- Service unavailability: Detailed error logging
- Validation failures: Clear compliance status reporting

## Performance

- **Async/await**: Non-blocking I/O for service calls
- **Concurrent validation**: Validates all assets in parallel
- **Headless browser**: Chromium runs in headless mode for speed
- **Timeout management**: 30s for extraction, 30s for SyncBrain, 60s for SyncCreate

## Monitoring

Logs all workflow stages:

```
✓ Extracted brand identity: Example Corp
✓ Generated campaign brief: campaign_123
✓ Generated 5 ad copies and 3 image prompts
✓ Validated all assets: 87.5% approval rate
```

## Future Enhancements

- [ ] Multi-page crawling for comprehensive brand analysis
- [ ] Competitor analysis integration
- [ ] A/B test variant generation
- [ ] Real-time creative performance prediction (integrate SyncValue LTV)
- [ ] Automated asset deployment to ad platforms (integrate SyncFlow)
- [ ] Brand voice consistency scoring
- [ ] Multilingual support
- [ ] Image extraction and analysis

## Architecture Alignment

This module follows KIKI Agent™ principles:

✅ **Clean Architecture**: Separation of domain, service, and infrastructure layers  
✅ **DDD**: Domain models (BrandIdentity, CampaignBrief, GeneratedAsset)  
✅ **Service Mesh**: HTTP/REST integration with SyncBrain, SyncCreate, SyncShield  
✅ **Type Safety**: Pydantic models with full type annotations  
✅ **Testing**: Comprehensive unit and integration tests  
✅ **Observability**: Structured logging with context

## Dependencies

| Package | Purpose |
|---------|---------|
| `playwright` | Headless browser automation |
| `beautifulsoup4` | HTML parsing |
| `httpx` | Async HTTP client for service calls |
| `pydantic` | Data validation and serialization |
| `lxml` | Fast XML/HTML parser for BeautifulSoup |

## Support

For issues or questions:
- See `/docs/AGENT_SPEC.md` for KIKI Agent architecture
- See `/docs/API_REFERENCE.md` for service APIs
- Check logs in `/logs/syncvalue/scraper.log`

---

**KIKI Agent™ SyncScrape** - Autonomous Brand Intelligence & Campaign Generation
