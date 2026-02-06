# PromptEngineer Integration with Council of Nine

## Overview

The existing **PromptEngineer** in SyncCreate is now **fully integrated** with the Council of Nine for `prompt_to_campaign` and `url_to_campaign` workflows.

## How It Works

### 1. PromptEngineer Class

Located: `services/synccreate/logic/prompt_engineer.py`

**Purpose**: Dynamically engineer high-quality Stable Diffusion prompts based on:
- **Audience segment**: luxury, tech, lifestyle
- **LTV score**: 0.0 - 1.0 (higher = more premium aesthetic)
- **Product description**: Brand-specific context

**Example Output**:
```
Input:
- audience_segment = "luxury"
- ltv_score = 0.9
- product_desc = "New Product Launch brand showcase"

Output:
"New Product Launch brand showcase, rich textures, gold accents, soft bokeh, 
cinematic, 8k, editorial photography, High-end, minimalist, professional, 
luxury lighting --no blurry, low quality, distorted hands, text, watermark"
```

### 2. Council of Nine Integration

The orchestrator calls SyncCreate with brand context:

```python
# From council_of_nine.py
image_prompts = await self.synccreate.generate_image_prompts(
    brand_data={
        "brand_name": "Tesla",
        "industry_profile": {
            "category": "SaaS & Software",
            "ltv_baseline": 800.0
        },
        "tone": "professional"
    },
    count=3
)
```

### 3. SyncCreate Processing

**Endpoint**: `POST /generate-image-prompts`

**Processing Flow**:
1. Extract brand context (name, industry, LTV, tone, colors)
2. Calculate **LTV score** from LTV baseline:
   ```python
   ltv_score = min(1.0, max(0.3, ltv_baseline / 250.0))
   
   Examples:
   - $50 LTV → 0.5 score → "vibrant, engaging, social-media style"
   - $800 LTV → 1.0 score → "cinematic, 8k, editorial photography"
   ```

3. Map industry to **audience segment**:
   ```python
   Industry                    → Audience Segment
   ─────────────────────────────────────────────
   E-commerce & Retail         → lifestyle
   SaaS & Software             → tech
   Mobile Gaming               → tech
   Professional Services       → luxury
   Financial Services          → luxury
   Health & Wellness           → lifestyle
   ```

4. **Call PromptEngineer** for each image:
   ```python
   engineered_prompt = prompt_engineer.craft_prompt(
       audience_segment="tech",
       ltv_score=0.9,
       product_desc="Tesla brand showcase"
   )
   ```

5. Return engineered prompts to Council of Nine

### 4. Real-World Example

**User Input**: 
```
"Launch product with $100k budget, target ROI 3x"
```

**Council of Nine Flow**:
```
1. Parse prompt → industry="General", ltv_baseline=$100
2. Calculate LTV score → 100/250 = 0.4
3. Map to audience → "lifestyle"
4. Call SyncCreate /generate-image-prompts
5. PromptEngineer crafts:
   
   "New Product Launch professional marketing image #1, 
   natural sunlight, candid, warm tones, vibrant, engaging, 
   social-media style, High-end, minimalist, professional, 
   luxury lighting --no blurry, low quality, distorted hands, 
   text, watermark"
```

## LTV-Based Aesthetic Mapping

| LTV Baseline | LTV Score | Aesthetic Style | Use Case |
|--------------|-----------|-----------------|----------|
| $25-50 | 0.3-0.5 | Vibrant, social-media style | Mobile gaming, casual e-commerce |
| $100-200 | 0.5-0.8 | Professional, engaging | SaaS B2C, health & wellness |
| $250-1000 | 0.8-1.0 | Cinematic, editorial | SaaS B2B, professional services |
| $1000+ | 1.0 | 8k, luxury, premium | Enterprise B2B, financial services |

## Audience Segment Modifiers

### Luxury
```
"rich textures, gold accents, soft bokeh"
Aesthetic: "cinematic, 8k, editorial photography" (if LTV > 0.8)
```

### Tech
```
"neon highlights, clean lines, futuristic"
Aesthetic: "cinematic, 8k, editorial photography" (if LTV > 0.8)
```

### Lifestyle
```
"natural sunlight, candid, warm tones"
Aesthetic: "vibrant, engaging, social-media style" (if LTV ≤ 0.8)
```

## API Endpoints

### Generate Ad Copies
```bash
curl -X POST http://localhost:8004/generate-copy \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "Tesla",
    "campaign_brief": {
      "target_audience": "B2B enterprise decision makers",
      "key_message": "Revolutionize your energy infrastructure",
      "tone": "professional"
    },
    "count": 5
  }'
```

### Generate Image Prompts (with PromptEngineer)
```bash
curl -X POST http://localhost:8004/generate-image-prompts \
  -H "Content-Type: application/json" \
  -d '{
    "brand_data": {
      "brand_name": "Tesla",
      "industry_profile": {
        "category": "SaaS & Software",
        "ltv_baseline": 800.0
      },
      "tone": "professional"
    },
    "count": 3
  }'
```

**Response**:
```json
{
  "image_prompts": [
    "Tesla product showcase, professional photography, neon highlights, clean lines, futuristic, cinematic, 8k, editorial photography, High-end, minimalist, professional, luxury lighting --no blurry, low quality, distorted hands, text, watermark",
    "Tesla brand lifestyle image, authentic customer experience, neon highlights, clean lines, futuristic, cinematic, 8k, editorial photography, High-end, minimalist, professional, luxury lighting --no blurry, low quality, distorted hands, text, watermark",
    "Tesla abstract brand identity, modern design, neon highlights, clean lines, futuristic, cinematic, 8k, editorial photography, High-end, minimalist, professional, luxury lighting --no blurry, low quality, distorted hands, text, watermark"
  ],
  "brand_name": "Tesla",
  "audience_segment": "tech",
  "ltv_score": 1.0,
  "count": 3
}
```

## Benefits

✅ **LTV-Optimized Creative**: Higher LTV → More premium aesthetics  
✅ **Industry-Specific Styling**: Each industry gets appropriate visual treatment  
✅ **Audience-Targeted**: Prompts adapt to luxury, tech, or lifestyle segments  
✅ **Consistent Quality**: Negative prompts filter out low-quality outputs  
✅ **Stable Diffusion Ready**: Prompts are optimized for SD 2.1+  

## Next Steps

1. **Test with real Stable Diffusion**: Connect to local SD instance or Stability AI API
2. **A/B Test Prompts**: Compare engineered vs. non-engineered prompt performance
3. **Expand Templates**: Add more audience segments and industry-specific modifiers
4. **Video Support**: Use `MultimediaPromptEngineer` for video campaign variations

## Summary

The **PromptEngineer now powers the entire Council of Nine creative generation pipeline**, ensuring that every campaign gets LTV-optimized, industry-appropriate, audience-targeted creative assets automatically. 🎨✨
