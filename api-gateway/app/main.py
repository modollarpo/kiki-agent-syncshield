"""KIKI Agent™ API Gateway.

Production baseline:
- Consistent service discovery via SERVICE_MAP
- Health aggregation endpoints for dashboards and CI
- Custom unauthenticated proxies for onboarding + selected flows
- JWT-gated generic proxy for protected service APIs
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from collections import defaultdict, deque
from typing import Any, Dict

import httpx
import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jwt import PyJWTError
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest


logger = logging.getLogger("kiki.api_gateway")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


app = FastAPI(title="KIKI Agent API Gateway")


allow_origins = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)


REQUEST_COUNT = Counter(
    "api_gateway_requests_total",
    "Total API Gateway requests",
    ["method", "endpoint"],
)


def _env_service_map() -> Dict[str, str]:
    """Allow overrides like SERVICE_SYNCBRAIN_URL=http://..."""
    defaults: Dict[str, str] = {
        "syncbrain": "http://syncbrain:8000",
        "syncvalue": "http://syncvalue:8000",
        "syncflow": "http://syncflow:8000",
        "synccreate": "http://synccreate:8000",
        "syncengage": "http://syncengage:8000",
        "syncshield": "http://syncshield:8000",
        "syncreflex": "http://syncreflex:8000",
        "synctwin": "http://synctwin:8000",
        "syncmultimodal": "http://syncmultimodal:8000",
        "explainability": "http://explainability-broker:8000",
        "acquisition": "http://acquisitionagent:8000",
        "syncportal": "http://syncportal:8000",
    }

    for key in list(defaults.keys()):
        env_key = f"SERVICE_{key.upper()}_URL"
        if os.getenv(env_key):
            defaults[key] = os.environ[env_key]
    return defaults


SERVICE_MAP = _env_service_map()


# Security config
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "")


def verify_jwt(request: Request) -> Dict[str, Any]:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def verify_internal_key(request: Request) -> None:
    if not INTERNAL_API_KEY:
        return
    provided = request.headers.get("x-internal-api-key", "")
    if provided != INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid internal API key")


def authorize_gateway_request(request: Request) -> Dict[str, Any]:
    """Authorize either via internal key (service-to-service) or via JWT (user-scoped)."""
    # Internal key wins: used by trusted backends like Next.js server routes.
    if INTERNAL_API_KEY and request.headers.get("x-internal-api-key") == INTERNAL_API_KEY:
        return {"sub": "internal"}
    return verify_jwt(request)


# Rate limiting: per-IP + per-endpoint (simple fixed window)
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_IP", "120"))
ENDPOINT_RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_ENDPOINT", "300"))
WINDOW = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
rate_limiters_ip = defaultdict(lambda: deque())
rate_limiters_endpoint = defaultdict(lambda: deque())


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    endpoint = request.url.path

    q_ip = rate_limiters_ip[ip]
    while q_ip and now - q_ip[0] > WINDOW:
        q_ip.popleft()
    if len(q_ip) >= RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "IP rate limit exceeded"})
    q_ip.append(now)

    q_ep = rate_limiters_endpoint[endpoint]
    while q_ep and now - q_ep[0] > WINDOW:
        q_ep.popleft()
    if len(q_ep) >= ENDPOINT_RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Endpoint rate limit exceeded"})
    q_ep.append(now)

    return await call_next(request)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("%s %s", request.method, request.url.path)
    return await call_next(request)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health/services")
async def services_health(request: Request):
    """Aggregated service health for dashboards. Optional internal-key gating."""
    verify_internal_key(request)

    async def probe(name: str, base: str):
        try:
            async with httpx.AsyncClient(timeout=2.5) as client:
                resp = await client.get(base + "/healthz")
                return name, {"ok": resp.status_code == 200, "status": resp.status_code}
        except Exception as e:
            return name, {"ok": False, "error": str(e)}

    tasks = [probe(name, base) for name, base in SERVICE_MAP.items()]
    results = await asyncio.gather(*tasks)
    return {"services": {k: v for k, v in results}}


@app.get("/openapi-aggregate")
async def openapi_aggregate(request: Request):
    verify_internal_key(request)

    async def fetch_openapi(url: str):
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                resp = await client.get(url + "/openapi.json")
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            return None
        return None

    results = await asyncio.gather(*[fetch_openapi(base) for base in SERVICE_MAP.values()])
    openapi = {
        "openapi": "3.0.0",
        "info": {"title": "KIKI API Aggregate", "version": "1.0.0"},
        "paths": {},
        "components": {},
    }
    for spec in results:
        if not spec or "paths" not in spec:
            continue
        openapi["paths"].update(spec.get("paths", {}))
        components = spec.get("components", {})
        for k, v in components.items():
            openapi["components"].setdefault(k, {}).update(v)
    return openapi


# --- Selected public proxies (used by dashboard/onboarding) ---


@app.get("/api/syncengage/events")
async def api_crm_event_log():
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{SERVICE_MAP['syncengage']}/events")
            return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/synccreate/generate")
async def api_generate_creative(request: Request):
    body = await request.json()
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{SERVICE_MAP['synccreate']}/generate", json=body)
            return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/synccreate/creatives")
async def api_creative_history():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{SERVICE_MAP['synccreate']}/creatives")
            return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/syncengage/{event}")
async def api_crm_event(event: str, request: Request):
    body = await request.json()
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(f"{SERVICE_MAP['syncengage']}/{event}", json=body)
            return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/impact_audit")
async def impact_audit(request: Request):
    """Onboarding impact audit. Routed to SyncPortal."""
    body = await request.json()
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(f"{SERVICE_MAP['syncportal']}/impact_audit", json=body)
            return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception as e:
        return JSONResponse(status_code=502, content={"error": str(e)})


# --- JWT-gated generic proxy ---


@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service: str, path: str, request: Request):
    _ = authorize_gateway_request(request)
    REQUEST_COUNT.labels(method=request.method, endpoint=f"/api/{service}/{path}").inc()
    if service not in SERVICE_MAP:
        raise HTTPException(404, "Service not found")

    url = f"{SERVICE_MAP[service]}/{path}"
    headers = dict(request.headers)
    data = await request.body()
    headers.pop("authorization", None)

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.request(request.method, url, headers=headers, content=data)

    try:
        content = resp.json()
    except Exception:
        content = {"raw": resp.text}
    return JSONResponse(status_code=resp.status_code, content=content)
