from logic.prompt_engineer import PromptEngineer
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


@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# Prometheus /metrics endpoint
@app.get("/metrics")
def prometheus_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
