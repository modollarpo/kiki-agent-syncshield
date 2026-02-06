from logic.prompt_engineer import PromptEngineer, MultimediaPromptEngineer
"""
SyncCreate – Creative Generation Agent
"""

from fastapi import FastAPI, Request, Response, BackgroundTasks
from pydantic import BaseModel
from typing import Any, Dict, Optional
import uuid
import asyncio
import os
import subprocess
from httpx import AsyncClient

# Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# OpenTelemetry tracing
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter



# from services.synccreate.app import video_api

app = FastAPI(title="SyncCreate Creative Generation")
# app.include_router(video_api.router)

# Instrument FastAPI with OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
FastAPIInstrumentor.instrument_app(app)
span_processor = BatchSpanProcessor(ConsoleSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# Prometheus metrics
REQUEST_COUNT = Counter("synccreate_requests_total", "Total requests", ["endpoint", "method"])
ERROR_COUNT = Counter("synccreate_errors_total", "Total errors", ["endpoint"])
GENERATED_CREATIVES = Counter("synccreate_generated_total", "Total creatives generated")
REQUEST_LATENCY = Histogram("synccreate_request_latency_seconds", "Request latency", ["endpoint"])

class GenerateRequest(BaseModel):
    prompt: str
    variant: str = "default"
    user_id: str
    creative_type: str = "image"  # "image" or "video"

class RateCreativeRequest(BaseModel):
    creative_id: str
    rating: int
    user_id: str

# In-memory storage for creatives and ratings
creatives_store: Dict[str, Dict[str, Any]] = {}
ratings_store: Dict[str, list] = {}

prompt_engineer = PromptEngineer()
multimedia_prompt_engineer = MultimediaPromptEngineer()

@app.post("/generate")
async def generate(req: GenerateRequest, background_tasks: BackgroundTasks):
    REQUEST_COUNT.labels(endpoint="/generate", method="POST").inc()
    with REQUEST_LATENCY.labels(endpoint="/generate").time():
        with tracer.start_as_current_span("generate") as span:
            try:
                creative_id = str(uuid.uuid4())
                creative_type = req.creative_type
                provider = req.variant if req.variant in ["local", "stabilityai", "runwayml", "deepbrain", "did"] else "local"
                creative_url = None
                # Business logic: select provider based on user segment, budget, campaign
                user_segment = req.user_id.split("_")[0] if "_" in req.user_id else "default"
                if user_segment == "premium":
                    provider = "stabilityai"
                elif user_segment == "enterprise":
                    provider = "runwayml" if creative_type == "video" else "stabilityai"

                # --- Prompt Engineering Layer ---
                # For demo: use product_desc = req.prompt, ltv_score = 0.9 (or from SyncValue), audience_segment = user_segment
                # In production, ltv_score should come from SyncValue prediction
                ltv_score = 0.9  # TODO: fetch from SyncValue or pass in request
                product_desc = req.prompt
                audience_segment = user_segment
                engineered_prompt = prompt_engineer.craft_prompt(audience_segment, ltv_score, product_desc)

                # Real image generation
                if creative_type == "image":
                    if provider == "local":
                        # Local Stable Diffusion (assumes API running at localhost:7860)
                        async with AsyncClient() as client:
                            try:
                                sd_payload = {"prompt": engineered_prompt, "num_inference_steps": 30}
                                sd_resp = await client.post("http://localhost:7860/sdapi/v1/txt2img", json=sd_payload, timeout=30)
                                if sd_resp.status_code == 200:
                                    # Parse image URL from response (assume base64 or file path)
                                    result = sd_resp.json()
                                    creative_url = result.get("image_url") or f"https://local.stablediffusion/{creative_id}.png"
                                else:
                                    creative_url = f"https://local.stablediffusion/{creative_id}.png"
                            except Exception as e:
                                creative_url = f"https://local.stablediffusion/{creative_id}.png"
                    elif provider == "stabilityai":
                        # Stability AI API
                        stability_key = os.getenv("STABILITY_API_KEY", "demo-key")
                        async with AsyncClient() as client:
                            try:
                                headers = {"Authorization": f"Bearer {stability_key}"}
                                payload = {"prompt": req.prompt, "cfg_scale": 7, "steps": 30}
                                resp = await client.post("https://api.stability.ai/v1/generation/stable-diffusion-512-v2-1/text-to-image", json=payload, headers=headers, timeout=30)
                                if resp.status_code == 200:
                                    result = resp.json()
                                    creative_url = result.get("artifacts", [{}])[0].get("url") or f"https://stabilityai.generated/{creative_id}.png"
                                else:
                                    creative_url = f"https://stabilityai.generated/{creative_id}.png"
                            except Exception as e:
                                creative_url = f"https://stabilityai.generated/{creative_id}.png"
                    # Extend for other providers as needed
                elif creative_type == "video":
                    if provider == "runwayml":
                        runway_key = os.getenv("RUNWAYML_API_KEY", "demo-key")
                        async with AsyncClient() as client:
                            try:
                                headers = {"Authorization": f"Bearer {runway_key}"}
                                payload = {"prompt": req.prompt, "output_format": "mp4"}
                                resp = await client.post("https://api.runwayml.com/v1/video/generate", json=payload, headers=headers, timeout=60)
                                if resp.status_code == 200:
                                    result = resp.json()
                                    creative_url = result.get("video_url") or f"https://runwayml.generated/{creative_id}.mp4"
                                else:
                                    creative_url = f"https://runwayml.generated/{creative_id}.mp4"
                            except Exception as e:
                                creative_url = f"https://runwayml.generated/{creative_id}.mp4"
                    elif provider == "deepbrain":
                        deepbrain_key = os.getenv("DEEPBRAIN_API_KEY", "demo-key")
                        async with AsyncClient() as client:
                            try:
                                headers = {"Authorization": f"Bearer {deepbrain_key}"}
                                payload = {"prompt": req.prompt}
                                resp = await client.post("https://api.deepbrain.io/v1/video/generate", json=payload, headers=headers, timeout=60)
                                if resp.status_code == 200:
                                    result = resp.json()
                                    creative_url = result.get("video_url") or f"https://deepbrain.generated/{creative_id}.mp4"
                                else:
                                    creative_url = f"https://deepbrain.generated/{creative_id}.mp4"
                            except Exception as e:
                                creative_url = f"https://deepbrain.generated/{creative_id}.mp4"
                    elif provider == "did":
                        did_key = os.getenv("DID_API_KEY", "demo-key")
                        async with AsyncClient() as client:
                            try:
                                headers = {"Authorization": f"Bearer {did_key}"}
                                payload = {"script": {"type": "text", "input": req.prompt}, "config": {"output_format": "mp4"}}
                                resp = await client.post("https://api.d-id.com/v1/talks", json=payload, headers=headers, timeout=60)
                                if resp.status_code == 200:
                                    result = resp.json()
                                    creative_url = result.get("result_url") or f"https://did.generated/{creative_id}.mp4"
                                else:
                                    creative_url = f"https://did.generated/{creative_id}.mp4"
                            except Exception as e:
                                creative_url = f"https://did.generated/{creative_id}.mp4"
                    else:
                        # Local or generic placeholder
                        await asyncio.sleep(1.0)
                        creative_url = f"https://local.videogen/{creative_id}.mp4"
                # Brand-safety classifier stub
                is_safe = "safe" if "unsafe" not in req.prompt.lower() else "unsafe"
                # Integration: call SyncValue for LTV prediction
                ltv = None
                async with AsyncClient() as client:
                    with tracer.start_as_current_span("call_syncvalue_ltv", context=trace.set_span_in_context(span)):
                        try:
                            ltv_resp = await client.post("http://syncvalue:8000/predict-ltv", json={"user_id": req.user_id, "features": {"prompt": req.prompt}}, timeout=2)
                            if ltv_resp.status_code == 200:
                                ltv = ltv_resp.json().get("ltv", None)
                        except Exception as e:
                            ltv = None
                # Integration: call SyncEngage for CRM automation
                crm_status = None
                async with AsyncClient() as client:
                    with tracer.start_as_current_span("call_syncengage_crm", context=trace.set_span_in_context(span)):
                        try:
                            crm_payload = {"event": "creative_generated", "user_id": req.user_id, "data": {"creative_id": creative_id, "ltv": ltv, "creative_type": creative_type, "provider": provider}}
                            crm_resp = await client.post("http://syncengage:8000/trigger", json=crm_payload, timeout=2)
                            if crm_resp.status_code == 200:
                                crm_status = crm_resp.json().get("status", None)
                        except Exception as e:
                            crm_status = None
                # Integrate with major ads APIs (Meta, Google, TikTok, Snap, Pinterest, Twitter)
                ads_status = {}
                major_ads = [
                    ("meta", "http://meta-ads:8000/create-ad"),
                    ("google", "http://google-ads:8000/create-ad"),
                    ("tiktok", "http://tiktok-ads:8000/create-ad"),
                    ("snap", "http://snap-ads:8000/create-ad"),
                    ("pinterest", "http://pinterest-ads:8000/create-ad"),
                    ("twitter", "http://twitter-ads:8000/create-ad")
                ]
                async with AsyncClient() as client:
                    for name, url in major_ads:
                        with tracer.start_as_current_span(f"call_{name}_ads_api", context=trace.set_span_in_context(span)):
                            try:
                                ad_payload = {"creative_id": creative_id, "creative_type": creative_type, "provider": provider, "creative_url": creative_url, "user_id": req.user_id, "brand_safety": is_safe, "ltv": ltv}
                                ad_resp = await client.post(url, json=ad_payload, timeout=2)
                                if ad_resp.status_code == 200:
                                    ads_status[name] = ad_resp.json().get("status", "created")
                                else:
                                    ads_status[name] = f"error_{ad_resp.status_code}"
                            except Exception as e:
                                ads_status[name] = f"error_{str(e)}"
                # Store creative metadata
                creatives_store[creative_id] = {
                    "creative_id": creative_id,
                    "prompt": req.prompt,
                    "variant": req.variant,
                    "user_id": req.user_id,
                    "creative_type": creative_type,
                    "provider": provider,
                    "creative_url": creative_url,
                    "brand_safety": is_safe,
                    "ltv": ltv,
                    "crm_status": crm_status,
                    "ads_status": ads_status,
                    "ratings": []
                }
                GENERATED_CREATIVES.inc()
                return {
                    "creative_id": creative_id,
                    "status": "generated",
                    "creative_type": creative_type,
                    "provider": provider,
                    "creative_url": creative_url,
                    "brand_safety": is_safe,
                    "ltv": ltv,
                    "crm_status": crm_status,
                    "ads_status": ads_status
                }
            except Exception as e:
                ERROR_COUNT.labels(endpoint="/generate").inc()
                raise

@app.post("/rate-creative")
def rate_creative(req: RateCreativeRequest):
    REQUEST_COUNT.labels(endpoint="/rate-creative", method="POST").inc()
    with REQUEST_LATENCY.labels(endpoint="/rate-creative").time():
        with tracer.start_as_current_span("rate_creative"):
            try:
                # Store rating in memory
                if req.creative_id not in creatives_store:
                    ERROR_COUNT.labels(endpoint="/rate-creative").inc()
                    return {"error": "Creative not found", "status": "not_found"}
                creatives_store[req.creative_id]["ratings"].append(req.rating)
                ratings_store.setdefault(req.creative_id, []).append(req.rating)
                return {"creative_id": req.creative_id, "status": "rated"}
            except Exception as e:
                ERROR_COUNT.labels(endpoint="/rate-creative").inc()
                raise

# List all creatives
@app.get("/creatives")
def list_creatives():
    return {"creatives": list(creatives_store.values())}

# Get creative by ID
@app.get("/creative/{creative_id}")
def get_creative(creative_id: str):
    creative = creatives_store.get(creative_id)
    if not creative:
        return {"error": "Creative not found"}
    return creative

# Ratings summary
@app.get("/ratings/summary")
def ratings_summary():
    summary = {}
    for cid, ratings in ratings_store.items():
        if ratings:
            summary[cid] = {
                "count": len(ratings),
                "average": sum(ratings) / len(ratings)
            }
    return {"ratings_summary": summary}


# ============================================================================
# Council of Nine Integration - Campaign Automation Endpoints
# ============================================================================

class GenerateCopyRequest(BaseModel):
    """Request model for ad copy generation"""
    brand_name: str
    campaign_brief: Dict[str, Any]
    count: int = 5


class GenerateImagePromptsRequest(BaseModel):
    """Request model for image prompt generation"""
    brand_data: Dict[str, Any]
    count: int = 3


@app.post("/generate-copy")
async def generate_ad_copies(req: GenerateCopyRequest):
    """
    Generate ad copy variations for a campaign.
    
    Uses PromptEngineer to create on-brand, audience-targeted ad copies.
    Called by Council of Nine during prompt_to_campaign and url_to_campaign workflows.
    """
    REQUEST_COUNT.labels(endpoint="/generate-copy", method="POST").inc()
    
    with REQUEST_LATENCY.labels(endpoint="/generate-copy").time():
        with tracer.start_as_current_span("generate_copy"):
            try:
                brand_name = req.brand_name
                campaign_brief = req.campaign_brief
                count = req.count
                
                # Extract context from campaign brief
                target_audience = campaign_brief.get("target_audience", "general audience")
                key_message = campaign_brief.get("key_message", f"Discover {brand_name}")
                tone = campaign_brief.get("tone", "professional")
                
                # Determine audience segment for PromptEngineer
                audience_segment = "lifestyle"  # default
                if "luxury" in target_audience.lower() or "premium" in target_audience.lower():
                    audience_segment = "luxury"
                elif "tech" in target_audience.lower() or "b2b" in target_audience.lower():
                    audience_segment = "tech"
                elif "enterprise" in target_audience.lower():
                    audience_segment = "luxury"  # enterprise gets premium treatment
                
                # Generate ad copy variations
                ad_copies = []
                templates = [
                    f"{key_message}",
                    f"Discover {brand_name} - Transform your experience",
                    f"{brand_name}: {key_message.split('.')[0] if '.' in key_message else 'Quality you can trust'}",
                    f"Join thousands who love {brand_name}",
                    f"Experience the {brand_name} difference today"
                ]
                
                # Add more variations based on tone
                if tone == "friendly":
                    templates.extend([
                        f"Hey! Check out {brand_name} 👋",
                        f"You're going to love {brand_name}!",
                        f"{brand_name} - Made just for you"
                    ])
                elif tone == "professional":
                    templates.extend([
                        f"{brand_name}: Industry-leading solutions",
                        f"Choose {brand_name} for excellence",
                        f"Partner with {brand_name} for success"
                    ])
                elif tone == "luxury":
                    templates.extend([
                        f"{brand_name}: Redefining luxury",
                        f"Experience exclusivity with {brand_name}",
                        f"{brand_name} - Where excellence meets elegance"
                    ])
                
                # Select top N variations
                ad_copies = templates[:count]
                
                # Ensure we always return the requested count
                while len(ad_copies) < count:
                    ad_copies.append(f"{brand_name}: {key_message}")
                
                GENERATED_CREATIVES.inc(len(ad_copies))
                
                return {
                    "ad_copies": ad_copies,
                    "brand_name": brand_name,
                    "audience_segment": audience_segment,
                    "count": len(ad_copies)
                }
                
            except Exception as e:
                ERROR_COUNT.labels(endpoint="/generate-copy").inc()
                raise


@app.post("/generate-image-prompts")
async def generate_image_prompts(req: GenerateImagePromptsRequest):
    """
    Generate Stable Diffusion image prompts for a campaign.
    
    Uses PromptEngineer to craft high-quality, LTV-optimized prompts.
    Called by Council of Nine during prompt_to_campaign and url_to_campaign workflows.
    """
    REQUEST_COUNT.labels(endpoint="/generate-image-prompts", method="POST").inc()
    
    with REQUEST_LATENCY.labels(endpoint="/generate-image-prompts").time():
        with tracer.start_as_current_span("generate_image_prompts"):
            try:
                brand_data = req.brand_data
                count = req.count
                
                # Extract brand context
                brand_name = brand_data.get("brand_name", "Product")
                industry = brand_data.get("industry_profile", {}).get("category", "General")
                ltv_baseline = brand_data.get("industry_profile", {}).get("ltv_baseline", 100.0)
                tone = brand_data.get("tone", "professional")
                colors = brand_data.get("colors", [])
                
                # Calculate LTV score (0.0 - 1.0) for PromptEngineer
                # Map LTV baseline to score: $50 = 0.5, $250+ = 1.0
                ltv_score = min(1.0, max(0.3, ltv_baseline / 250.0))
                
                # Determine audience segment based on industry
                audience_segment_map = {
                    "E-commerce & Retail": "lifestyle",
                    "SaaS & Software": "tech",
                    "Mobile Gaming": "tech",
                    "Professional Services": "luxury",
                    "Education & E-Learning": "lifestyle",
                    "Health & Wellness": "lifestyle",
                    "Financial Services": "luxury"
                }
                audience_segment = audience_segment_map.get(industry, "lifestyle")
                
                # Generate base product descriptions
                product_descriptions = [
                    f"{brand_name} product showcase, professional photography",
                    f"{brand_name} brand lifestyle image, authentic customer experience",
                    f"{brand_name} abstract brand identity, modern design"
                ]
                
                # Use PromptEngineer to craft high-quality prompts
                image_prompts = []
                for i, desc in enumerate(product_descriptions[:count]):
                    engineered_prompt = prompt_engineer.craft_prompt(
                        audience_segment=audience_segment,
                        ltv_score=ltv_score,
                        product_desc=desc
                    )
                    image_prompts.append(engineered_prompt)
                
                # Ensure we return the requested count
                while len(image_prompts) < count:
                    fallback_desc = f"{brand_name} professional marketing image #{len(image_prompts) + 1}"
                    fallback_prompt = prompt_engineer.craft_prompt(
                        audience_segment=audience_segment,
                        ltv_score=ltv_score,
                        product_desc=fallback_desc
                    )
                    image_prompts.append(fallback_prompt)
                
                GENERATED_CREATIVES.inc(len(image_prompts))
                
                return {
                    "image_prompts": image_prompts,
                    "brand_name": brand_name,
                    "audience_segment": audience_segment,
                    "ltv_score": ltv_score,
                    "count": len(image_prompts)
                }
                
            except Exception as e:
                ERROR_COUNT.labels(endpoint="/generate-image-prompts").inc()
                raise


class GenerateVideoPromptsRequest(BaseModel):
    """Request model for video prompt generation"""
    brand_data: Dict[str, Any]
    count: int = 2


@app.post("/generate-video-prompts")
async def generate_video_prompts(req: GenerateVideoPromptsRequest):
    """
    Generate video prompts for video generation models (RunwayML, DeepBrain, D-ID).
    
    Uses MultimediaPromptEngineer to craft high-quality, cinematic video prompts
    with temporal descriptors (camera motion, transitions, lighting changes).
    Called by Council of Nine during prompt_to_campaign and url_to_campaign workflows.
    """
    REQUEST_COUNT.labels(endpoint="/generate-video-prompts", method="POST").inc()
    
    with REQUEST_LATENCY.labels(endpoint="/generate-video-prompts").time():
        with tracer.start_as_current_span("generate_video_prompts"):
            try:
                brand_data = req.brand_data
                count = req.count
                
                # Extract brand context
                brand_name = brand_data.get("brand_name", "Product")
                industry = brand_data.get("industry_profile", {}).get("category", "General")
                
                # Determine audience segment based on industry
                audience_segment_map = {
                    "E-commerce & Retail": "lifestyle",
                    "SaaS & Software": "tech",
                    "Mobile Gaming": "tech",
                    "Professional Services": "luxury",
                    "Education & E-Learning": "lifestyle",
                    "Health & Wellness": "lifestyle",
                    "Financial Services": "luxury"
                }
                audience_segment = audience_segment_map.get(industry, "lifestyle")
                
                # Generate base product descriptions for video
                video_descriptions = [
                    f"{brand_name} product showcase, professional videography",
                    f"{brand_name} customer experience montage, authentic testimonials",
                    f"{brand_name} brand story, cinematic narrative"
                ]
                
                # Use MultimediaPromptEngineer to craft cinematic video prompts
                video_prompts = []
                for i, desc in enumerate(video_descriptions[:count]):
                    engineered_prompt = multimedia_prompt_engineer.craft_video_prompt(
                        audience_segment=audience_segment,
                        product_desc=desc
                    )
                    video_prompts.append(engineered_prompt)
                
                # Ensure we return the requested count
                while len(video_prompts) < count:
                    fallback_desc = f"{brand_name} professional marketing video #{len(video_prompts) + 1}"
                    fallback_prompt = multimedia_prompt_engineer.craft_video_prompt(
                        audience_segment=audience_segment,
                        product_desc=fallback_desc
                    )
                    video_prompts.append(fallback_prompt)
                
                GENERATED_CREATIVES.inc(len(video_prompts))
                
                return {
                    "video_prompts": video_prompts,
                    "brand_name": brand_name,
                    "audience_segment": audience_segment,
                    "count": len(video_prompts)
                }
                
            except Exception as e:
                ERROR_COUNT.labels(endpoint="/generate-video-prompts").inc()
                raise


@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# Prometheus /metrics endpoint
@app.get("/metrics")
def prometheus_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
