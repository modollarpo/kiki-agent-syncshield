# BYOC API Guide - Bring Your Own Creative

Users can provide their own creative assets (ad copies, images, videos) instead of relying entirely on AI generation. This gives complete creative control while still leveraging KIKI Agent's deployment, optimization, and LTV prediction capabilities.

## Asset Types

KIKI Agent supports four types of user-provided assets:

| Asset Type | Description | Format |
|------------|-------------|--------|
| **Ad Copies** | Text-based ad content | Array of strings |
| **Images** | Product photos, lifestyle images | URLs or base64-encoded data |
| **Videos** | Video content for campaigns | URLs or file paths |
| **Descriptions** | Metadata/captions for visual assets | Array of strings |

## Asset Source Tracking

Every campaign tracks where assets came from:

- **`generated`** - All assets created by AI
- **`user_provided`** - All assets provided by user
- **`hybrid`** - Mix of user-provided and AI-generated

## API Usage

### Prompt-to-Campaign with User Assets

```bash
curl -X POST http://syncvalue:8002/prompt-to-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Launch SaaS product, $50k budget, 4x ROI target",
    "auto_deploy": false,
    "user_assets": {
      "ad_copies": [
        "🚀 Ship your SaaS in 30 days, not 6 months",
        "Join 10,000+ founders who launched faster",
        "Stop overthinking. Start building today."
      ],
      "images": [
        "https://cdn.mysite.com/hero.jpg",
        "https://cdn.mysite.com/product.jpg"
      ],
      "videos": [
        "https://vimeo.com/mybrand/demo-30s"
      ],
      "descriptions": [
        "Hero image with product screenshot",
        "Product features grid layout",
        "30-second product demo video"
      ]
    }
  }'
```

### URL-to-Campaign with User Assets

```bash
curl -X POST http://syncvalue:8002/url-to-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://mystore.com",
    "auto_deploy": false,
    "user_assets": {
      "ad_copies": [
        "Limited Time: 50% Off All Products",
        "Free Shipping on Orders Over $50"
      ],
      "images": [
        "https://s3.amazonaws.com/mystore/campaign-q1.jpg"
      ]
    }
  }'
```

## Response Format

```json
{
  "deployment_id": "campaign_a3f9e2d1c8b7",
  "brand_name": "MyBrand",
  "assets_source": "hybrid",
  "budget": 50000,
  "target_roi": 4.0,
  "max_cpa": 62.50,
  
  "ad_copies": [
    "AI-generated ad copy 1",
    "AI-generated ad copy 2"
  ],
  "user_provided_ad_copies": [
    "🚀 Ship your SaaS in 30 days",
    "Join 10,000+ founders"
  ],
  
  "image_prompts": [
    "AI-generated SD prompt for product image"
  ],
  "user_provided_images": [
    "https://cdn.mysite.com/hero.jpg",
    "https://cdn.mysite.com/product.jpg"
  ],
  
  "video_prompts": [],
  "user_provided_videos": [
    "https://vimeo.com/mybrand/demo-30s"
  ],
  
  "user_provided_descriptions": [
    "Hero image with product screenshot",
    "Product features grid layout",
    "30-second product demo video"
  ],
  
  "brand_safe": true,
  "compliance_status": "approved",
  "deployment_status": "draft"
}
```

## Use Cases

### 1. Marketing Agency Workflow
**Scenario**: Agency has complete creative package, needs deployment & optimization

```json
{
  "user_assets": {
    "ad_copies": ["Agency-crafted headlines..."],
    "images": ["Professional photoshoot assets..."],
    "videos": ["Produced video content..."]
  }
}
```

**Result**: `assets_source: "user_provided"` - KIKI handles deployment, LTV optimization, brand safety

### 2. Hybrid Creative Workflow
**Scenario**: User has hero image, wants AI to generate variations

```json
{
  "user_assets": {
    "images": ["https://cdn.example.com/hero.jpg"]
  }
}
```

**Result**: `assets_source: "hybrid"` - AI generates ad copies, image prompts, videos

### 3. AI-First with User Overrides
**Scenario**: Let AI generate, but override specific elements

```json
{
  "user_assets": {
    "ad_copies": ["Specific headline required by legal team"]
  }
}
```

**Result**: Uses user headline, AI generates all other assets

### 4. Complete Automation
**Scenario**: No user assets provided

```json
{
  "user_assets": null
}
```

**Result**: `assets_source: "generated"` - Full AI generation

## Asset Processing Logic

### AI Generation Skip Rules

```python
if user_assets.get("ad_copies"):
    # Skip ad copy generation
    ad_copies = []
    logger.info("⏭️  Skipping ad copy generation (user-provided)")
else:
    # Generate 5 ad copies via SyncCreate
    ad_copies = await synccreate.generate_ad_copies(...)
    logger.info(f"✅ Generated {len(ad_copies)} ad copies")
```

### Brand Safety Validation

User-provided ad copies still undergo brand safety validation:

```python
# Validate ALL ad copies (user + AI)
all_copies = user_provided_ad_copies + ad_copies
safety_check = await syncshield.validate_brand_safety(all_copies, brand_name)
```

### Deployment Integration

SyncFlow receives both user-provided and AI-generated assets:

```python
deployment_payload = {
    "ad_copies": deployment.ad_copies,
    "user_ad_copies": deployment.user_provided_ad_copies,
    "images": deployment.user_provided_images,
    "image_prompts": deployment.image_prompts,  # For on-demand generation
    ...
}
```

## Image Formats

### URLs (Recommended)
```json
{
  "images": [
    "https://cdn.example.com/image.jpg",
    "https://s3.amazonaws.com/bucket/image.png"
  ]
}
```

### Base64 Encoded
```json
{
  "images": [
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEA..."
  ]
}
```

## Video Formats

### Video URLs
```json
{
  "videos": [
    "https://vimeo.com/123456789",
    "https://youtube.com/watch?v=abc123",
    "https://s3.amazonaws.com/mybrand/video.mp4"
  ]
}
```

### Local Files (for upload workflows)
```json
{
  "videos": [
    "/tmp/uploaded_campaign_video.mp4"
  ]
}
```

## Cost Optimization

BYOC reduces AI generation costs:

| Scenario | AI Calls | Est. Cost/Campaign |
|----------|----------|-------------------|
| **Full AI** | 10+ API calls | $2.50 - $5.00 |
| **Hybrid** | 3-5 API calls | $0.75 - $1.50 |
| **Complete BYOC** | 0-1 API calls | $0.00 - $0.25 |

## Examples by Industry

### E-Commerce
```json
{
  "user_assets": {
    "images": ["Product catalog photos from photoshoot"],
    "descriptions": ["Seasonal campaign - Winter 2026 collection"]
  }
}
```

### SaaS
```json
{
  "user_assets": {
    "ad_copies": ["Messaging approved by product marketing"],
    "videos": ["Product demo from engineering team"]
  }
}
```

### Mobile Gaming
```json
{
  "user_assets": {
    "videos": ["Gameplay footage from QA"],
    "images": ["App store screenshots"]
  }
}
```

### B2B Enterprise
```json
{
  "user_assets": {
    "ad_copies": ["Compliance-approved messaging"],
    "descriptions": ["Campaign targeting Fortune 500 CTOs"],
    "images": ["Customer logo grid for social proof"]
  }
}
```

## Error Handling

### Invalid Asset URLs
```json
{
  "error": "image_validation_failed",
  "message": "Unable to access: https://invalid-url.com/image.jpg",
  "field": "user_assets.images[0]"
}
```

### Brand Safety Violations
```json
{
  "deployment_status": "safety_hold",
  "compliance_status": "review_required",
  "message": "User-provided ad copy contains restricted content"
}
```

### Missing Required Fields
```json
{
  "error": "invalid_request",
  "message": "user_assets.descriptions length must match user_assets.images length"
}
```

## Best Practices

1. **Always Provide Descriptions** - Context improves deployment optimization
2. **Use CDN URLs** - Faster processing than base64 encoding
3. **Validate Before Upload** - Check image dimensions, file sizes, formats
4. **Mix Strategically** - Combine best of AI + human creativity
5. **Track Performance** - Compare `generated` vs `user_provided` vs `hybrid` campaigns

## Integration Patterns

### React Frontend Example
```javascript
const deployWithUserAssets = async () => {
  const response = await fetch('http://syncvalue:8002/prompt-to-campaign', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt: "Launch mobile game, $100k budget",
      user_assets: {
        images: uploadedImages.map(img => img.url),
        ad_copies: adCopyInputs.map(input => input.value),
        descriptions: descriptionInputs.map(input => input.value)
      }
    })
  });
  
  const deployment = await response.json();
  console.log(`Assets: ${deployment.assets_source}`);
};
```

### Python SDK Example
```python
from kiki_sdk import CouncilOfNine

council = CouncilOfNine()

deployment = await council.prompt_to_campaign(
    prompt="SaaS product launch, $50k budget",
    user_assets={
        "ad_copies": [
            "Headline from marketing team",
            "CTO-approved technical messaging"
        ],
        "images": [
            "https://cdn.mysite.com/hero.jpg"
        ]
    }
)

print(f"Source: {deployment.assets_source}")
```

## Next Steps

- See [example_byoc_campaign.py](../services/syncvalue/example_byoc_campaign.py) for live examples
- Review [API_REFERENCE.md](./API_REFERENCE.md) for complete endpoint documentation
- Check [ARCHITECTURE.md](./ARCHITECTURE.md) for system design details
