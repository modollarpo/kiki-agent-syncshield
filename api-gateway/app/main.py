# --- Custom endpoint: CRM Event Log (SyncEngage, REST proxy) ---
@app.get("/api/syncengage/events")
async def api_crm_event_log():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{SERVICE_MAP['syncengage']}/events")
            return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
import asyncio
# Example route aggregation (proxy pattern)
@app.get("/openapi-aggregate")
async def openapi_aggregate():
    """Aggregate OpenAPI specs from all backend services."""
    with tracer.start_as_current_span("openapi_aggregate"):
        async def fetch_openapi(url):
            try:
                async with httpx.AsyncClient(timeout=3) as client:
                    resp = await client.get(url + "/openapi.json")
                    if resp.status_code == 200:
                        return resp.json()
            except Exception:
                return None
        tasks = [fetch_openapi(base) for base in SERVICE_MAP.values()]
        results = await asyncio.gather(*tasks)
        # Merge paths/components (simple union, no conflict resolution)
        openapi = {"openapi": "3.0.0", "info": {"title": "KIKI API Aggregate", "version": "1.0.0"}, "paths": {}, "components": {}}
        for spec in results:
            if not spec or "paths" not in spec:
                continue
            openapi["paths"].update(spec["paths"])
            if "components" in spec:
                for k, v in spec["components"].items():
                    openapi["components"].setdefault(k, {}).update(v)
        return openapi
from fastapi import Response
# Prometheus metrics (simple counter example)
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter("api_gateway_requests_total", "Total API Gateway requests", ["method", "endpoint"])
"""
API Gateway for KIKI Agent™
Aggregates all service APIs, handles authentication and rate limiting.
"""

from fastapi import FastAPI, Request, HTTPException, Depends
import logging
import time
from collections import defaultdict, deque
from fastapi.responses import JSONResponse
import httpx
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
import os
import jwt
from jwt import PyJWTError



app = FastAPI(title="KIKI Agent API Gateway")

# OpenTelemetry tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
FastAPIInstrumentor.instrument_app(app)
span_processor = BatchSpanProcessor(ConsoleSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# Advanced rate limiting: per-IP, per-user (JWT), per-endpoint
RATE_LIMIT = 60
USER_RATE_LIMIT = 30
ENDPOINT_RATE_LIMIT = 100
WINDOW = 60  # seconds
rate_limiters_ip = defaultdict(lambda: deque())
rate_limiters_user = defaultdict(lambda: deque())
rate_limiters_endpoint = defaultdict(lambda: deque())

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    with tracer.start_as_current_span("rate_limit_middleware"):
        ip = request.client.host
        now = time.time()
        endpoint = request.url.path
        # Per-IP
        q_ip = rate_limiters_ip[ip]
        while q_ip and now - q_ip[0] > WINDOW:
            q_ip.popleft()
        if len(q_ip) >= RATE_LIMIT:
            return JSONResponse(status_code=429, content={"detail": "IP rate limit exceeded"})
        q_ip.append(now)
        # Per-user (JWT sub)
        user = None
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            try:
                payload = jwt.decode(auth.split(" ", 1)[1], JWT_SECRET, algorithms=[JWT_ALGORITHM])
                user = payload.get("sub")
            except Exception:
                pass
        if user:
            q_user = rate_limiters_user[user]
            while q_user and now - q_user[0] > WINDOW:
                q_user.popleft()
            if len(q_user) >= USER_RATE_LIMIT:
                return JSONResponse(status_code=429, content={"detail": "User rate limit exceeded"})
            q_user.append(now)
        # Per-endpoint
        q_ep = rate_limiters_endpoint[endpoint]
        while q_ep and now - q_ep[0] > WINDOW:
            q_ep.popleft()
        if len(q_ep) >= ENDPOINT_RATE_LIMIT:
            return JSONResponse(status_code=429, content={"detail": "Endpoint rate limit exceeded"})
        q_ep.append(now)
        response = await call_next(request)
        return response

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    with tracer.start_as_current_span("log_requests"):
        logging.info(f"{request.method} {request.url.path} from {request.client.host}")
        response = await call_next(request)
        return response

# JWT secret and algorithm (in production, use env var and strong secret)
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_ALGORITHM = "HS256"

def verify_jwt(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# Example route aggregation (proxy pattern)
SERVICE_MAP = {
    "syncbrain": "http://syncbrain:8000",
    "syncvalue": "http://syncvalue:8000",
    "syncflow": "http://syncflow:8000",
    "synccreate": "http://synccreate:8000",
    "syncengage": "http://syncengage:8000",
    "syncshield": "http://syncshield:8000"
}



# --- Custom endpoint: Creative Generation (SyncCreate, REST/gRPC hybrid) ---
@app.post("/api/synccreate/generate")
async def api_generate_creative(request: Request):
    body = await request.json()
    # Option 1: REST proxy
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{SERVICE_MAP['synccreate']}/generate", json=body)
            return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# --- Custom endpoint: CRM Event Trigger (SyncEngage, REST proxy) ---
@app.post("/api/syncengage/{event}")
async def api_crm_event(event: str, request: Request):
    body = await request.json()
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{SERVICE_MAP['syncengage']}/{event}", json=body)
            return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- Custom endpoint: Creative History (SyncCreate, REST proxy) ---
@app.get("/api/synccreate/creatives")
async def api_creative_history():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{SERVICE_MAP['synccreate']}/creatives")
            return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Fallback proxy for all other services
@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request, payload: dict = Depends(verify_jwt)):
    with tracer.start_as_current_span("gateway_proxy"):
        REQUEST_COUNT.labels(method=request.method, endpoint=f"/api/{service}/{path}").inc()
        if service not in SERVICE_MAP:
            raise HTTPException(404, "Service not found")
        url = f"{SERVICE_MAP[service]}/{path}"
        method = request.method
        headers = dict(request.headers)
        data = await request.body()
        headers.pop("authorization", None)
        async with httpx.AsyncClient() as client:
            resp = await client.request(method, url, headers=headers, content=data)
        return JSONResponse(status_code=resp.status_code, content=resp.json())

@app.get("/healthz")
def health_check():
    return {"status": "ok"}
