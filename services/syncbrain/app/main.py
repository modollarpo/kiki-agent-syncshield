

"""
SyncBrain – LLM Orchestration Service
Production-grade FastAPI app for orchestrating LLM-based strategies.
"""

# Ensure workspace root is in sys.path for imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))


from fastapi import FastAPI, Request, HTTPException, Response, WebSocket, WebSocketDisconnect, Query, Body
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field, ValidationError
from typing import Any, Dict, List, Optional
import httpx
import logging
import os
import openai
import threading
import grpc
import asyncio
from concurrent import futures
from shared.types.python.brain import brain_pb2_grpc, brain_pb2
import csv
import io
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from fastapi import BackgroundTasks
from fastapi_limiter import FastAPILimiter
import uuid

# Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# OpenTelemetry tracing
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


app = FastAPI(title="SyncBrain LLM Orchestrator", description="LLM-based strategy orchestration with context, rules, and OpenAI integration.")

# Instrument FastAPI with OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
FastAPIInstrumentor.instrument_app(app)
span_processor = BatchSpanProcessor(ConsoleSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# Prometheus metrics
REQUEST_COUNT = Counter("syncbrain_requests_total", "Total requests", ["endpoint", "method"])
ERROR_COUNT = Counter("syncbrain_errors_total", "Total errors", ["endpoint"])
STRATEGY_PLANS = Counter("syncbrain_strategy_plans_total", "Total strategies planned")
REQUEST_LATENCY = Histogram("syncbrain_request_latency_seconds", "Request latency", ["endpoint"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("syncbrain")

# In-memory conversation/context manager
conversation_memory: Dict[str, List[Dict[str, Any]]] = {}

# In-memory log store for demo
LOG_STORE = [
    {"timestamp": "2026-01-25T09:00:00Z", "level": "INFO", "message": "SyncBrain started."},
    {"timestamp": "2026-01-25T09:01:00Z", "level": "DEBUG", "message": "Strategy planned."},
]

# User management
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
def bcrypt_safe(password: str) -> str:
    # Truncate password to 72 bytes for bcrypt
    b = password.encode('utf-8')[:72]
    return b.decode('utf-8', errors='ignore')

# Use a short ASCII password for admin to avoid bcrypt issues in tests
ADMIN_PASSWORD = "adminpass"  # ASCII, <72 chars
USER_DB = {"admin": {"username": "admin", "password": pwd_context.hash(ADMIN_PASSWORD), "role": "admin"}}
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# In-memory email verification and password reset tokens
EMAIL_VERIFICATION = {}
PASSWORD_RESET = {}
AUDIT_LOG = []

# Rules/guardrails
def validate_strategy_input(context: Dict[str, Any]) -> bool:
    # Example: require at least one key in context
    return bool(context)

def filter_llm_output(output: str) -> str:
    # Example: block certain words (simple guardrail)
    blocked = ["hack", "exploit"]
    for word in blocked:
        if word in output.lower():
            return "[REDACTED]"
    return output

class StrategyRequest(BaseModel):
    user_id: str = Field(..., json_schema_extra={"example": "user_123"})
    context: Dict[str, Any] = Field(..., json_schema_extra={"example": {"goal": "maximize LTV"}})

class StrategyResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "planned"})
    user_id: str = Field(..., json_schema_extra={"example": "user_123"})
    plan: Optional[str] = Field(None, json_schema_extra={"example": "Increase ad spend on high-LTV segments."})

class AgentCoordinationRequest(BaseModel):
    agents: List[str] = Field(..., json_schema_extra={"example": ["syncvalue", "syncflow"]})
    task: str = Field(..., json_schema_extra={"example": "run_campaign"})
    context: Dict[str, Any] = Field(..., json_schema_extra={"example": {"budget": 1000}})

class PerformanceEvalRequest(BaseModel):
    session_id: str = Field(..., json_schema_extra={"example": "sess_456"})
    metrics: Dict[str, Any] = Field(..., json_schema_extra={"example": {"roi": 1.2}})

@app.post("/plan-strategy", response_model=StrategyResponse, responses={
    200: {"description": "LLM-generated plan", "content": {"application/json": {"example": {"status": "planned", "user_id": "user_123", "plan": "Increase ad spend on high-LTV segments."}}}},
    400: {"description": "Invalid input"},
    500: {"description": "LLM error"}
})
def plan_strategy(req: StrategyRequest):
    """Plan a revenue strategy using LLMs and OpenAI."""
    REQUEST_COUNT.labels(endpoint="/plan-strategy", method="POST").inc()
    with REQUEST_LATENCY.labels(endpoint="/plan-strategy").time():
        with tracer.start_as_current_span("plan_strategy"):
            try:
                if not validate_strategy_input(req.context):
                    logger.warning(f"Invalid context for user {req.user_id}")
                    ERROR_COUNT.labels(endpoint="/plan-strategy").inc()
                    raise HTTPException(status_code=400, detail="Context is required.")
                # Store context in memory
                conversation_memory.setdefault(req.user_id, []).append({"context": req.context})
                # Call OpenAI (real integration, v1+ API)
                openai.api_key = os.getenv("OPENAI_API_KEY", "demo-key")
                prompt = f"User context: {req.context}. Generate a revenue plan."
                try:
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": "You are a revenue strategy expert."},
                                  {"role": "user", "content": prompt}],
                        max_tokens=64,
                        temperature=0.7
                    )
                    plan = response.choices[0].message.content.strip()
                except Exception as e:
                    logger.error(f"OpenAI error: {e}")
                    ERROR_COUNT.labels(endpoint="/plan-strategy").inc()
                    raise HTTPException(status_code=500, detail="LLM service error.")
                plan = filter_llm_output(plan)
                # Store plan in memory
                conversation_memory[req.user_id].append({"plan": plan})
                logger.info(f"Planned strategy for {req.user_id}: {plan}")
                STRATEGY_PLANS.inc()
                return {"status": "planned", "user_id": req.user_id, "plan": plan}
            except ValidationError as ve:
                logger.error(f"Validation error: {ve}")
                ERROR_COUNT.labels(endpoint="/plan-strategy").inc()
                raise HTTPException(status_code=400, detail=f"Validation error: {ve}")
            except HTTPException as he:
                logger.error(f"HTTP error: {he.detail}")
                ERROR_COUNT.labels(endpoint="/plan-strategy").inc()
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                ERROR_COUNT.labels(endpoint="/plan-strategy").inc()
                raise HTTPException(status_code=500, detail=str(e))
# Custom OpenAPI schema with examples
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/coordinate-agents")
def coordinate_agents(req: AgentCoordinationRequest):

    """Coordinate downstream agents via REST calls (service mesh/gateway)."""
    logger.info(f"Coordinating agents {req.agents} for task {req.task}")
    results = {}
    agent_endpoints = {
        "syncvalue": os.getenv("SYNCVALUE_URL", "http://syncvalue:8000/predict-ltv"),
        "syncflow": os.getenv("SYNCFLOW_URL", "http://syncflow:8000/execute-bid"),
        "synccreate": os.getenv("SYNCCREATE_URL", "http://synccreate:8000/generate"),
    }
    for agent in req.agents:
        url = agent_endpoints.get(agent)
        if not url:
            results[agent] = {"error": "Unknown agent"}
            continue
        try:
            payload = {"context": req.context, "task": req.task}
            if agent == "synccreate":
                payload = {"prompt": req.context.get("creative_prompt", "Default creative"), "user_id": req.context.get("user_id", "system")}
            elif agent == "syncvalue":
                payload = {"user_id": req.context.get("user_id", "system"), "features": req.context}
            elif agent == "syncflow":
                payload = {"bid_request": req.context}
            with httpx.Client(timeout=5.0) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                results[agent] = resp.json()
        except Exception as e:
            logger.error(f"Error calling {agent}: {e}")
            results[agent] = {"error": str(e)}
    return {"status": "coordinated", "results": results}

@app.post("/evaluate-performance")
def evaluate_performance(req: PerformanceEvalRequest):
    """Evaluate agent performance and update memory."""
    # TODO: Store metrics, update context
    logger.info(f"Evaluating performance for session {req.session_id}")
    return {"status": "evaluated", "session_id": req.session_id}

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.post("/register")
def register(username: str = Body(...), password: str = Body(...), role: str = Body("analyst")):
    if username in USER_DB:
        return {"error": "User already exists"}
    USER_DB[username] = {"username": username, "password": pwd_context.hash(bcrypt_safe(password)), "role": role}
    return {"msg": "User registered"}

@app.post("/login")
def login(username: str = Body(...), password: str = Body(...)):
    user = USER_DB.get(username)
    if not user or not pwd_context.verify(password, user["password"]):
        return {"error": "Invalid credentials"}
    access_token = jwt.encode({
        "sub": username,
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_role(role: str):
    def role_checker(user=Depends(get_current_user)):
        if user.get("role") != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return role_checker

@app.get("/logs", dependencies=[Depends(require_role("admin"))])
def get_logs(level: str = Query(None), start: str = Query(None), end: str = Query(None), keyword: str = Query(None), page: int = Query(1), page_size: int = Query(50)):
    # Filter logs
    logs = LOG_STORE
    if level:
        logs = [l for l in logs if l["level"] == level]
    if start:
        start_dt = datetime.fromisoformat(start)
        logs = [l for l in logs if datetime.fromisoformat(l["timestamp"]) >= start_dt]
    if end:
        end_dt = datetime.fromisoformat(end)
        logs = [l for l in logs if datetime.fromisoformat(l["timestamp"]) <= end_dt]
    if keyword:
        logs = [l for l in logs if keyword.lower() in l["message"].lower()]
    # Pagination
    total = len(logs)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    logs_page = logs[start_idx:end_idx]
    return {"total": total, "page": page, "page_size": page_size, "logs": logs_page}

@app.get("/logs/export", dependencies=[Depends(require_role("admin"))])
def export_logs(format: str = Query("csv")):
    logs = LOG_STORE
    if format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["timestamp", "level", "message"])
        writer.writeheader()
        writer.writerows(logs)
        return StreamingResponse(io.BytesIO(output.getvalue().encode()), media_type="text/csv")
    return JSONResponse(content=logs)

@app.get("/analytics", dependencies=[Depends(require_role("analyst"))])
def get_analytics(window: str = Query("24h")):
    # Demo: support time window (e.g., "24h", "7d")
    now = datetime.utcnow()
    if window.endswith("h"):
        hours = int(window[:-1])
        start = now - timedelta(hours=hours)
    elif window.endswith("d"):
        days = int(window[:-1])
        start = now - timedelta(days=days)
    else:
        start = now - timedelta(hours=24)
    # Filter logs for analytics (demo)
    logs = [l for l in LOG_STORE if datetime.fromisoformat(l["timestamp"]) >= start]
    return {
        "total_strategies": len(logs),
        "avg_latency_ms": 120,
        "error_rate": 0.01,
        "users": 10
    }

@app.get("/settings", dependencies=[Depends(require_role("admin"))])
def get_settings():
    # Demo: dashboard config
    return {
        "log_levels": ["DEBUG", "INFO", "WARNING", "ERROR"],
        "retention_days": 30,
        "default_page_size": 50
    }

# Custom OpenAPI schema with examples
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema
app.openapi = custom_openapi

# --- Clean Architecture: UseCase Layer ---
from services.syncbrain.internal.usecases.orchestrate import orchestrate_strategy

# gRPC server implementation
class StrategyOrchestratorServicer(brain_pb2_grpc.StrategyOrchestratorServicer):
    def Orchestrate(self, request, context):
        # Delegate to usecase logic
        actions, status = orchestrate_strategy(request.campaign_id, list(request.user_ids), dict(request.context))
        return brain_pb2.OrchestrateResponse(campaign_id=request.campaign_id, actions=actions, status=status)

def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    brain_pb2_grpc.add_StrategyOrchestratorServicer_to_server(StrategyOrchestratorServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

@app.on_event("startup")
def start_grpc_server():
    threading.Thread(target=serve_grpc, daemon=True).start()

@app.on_event("startup")
async def startup():
    # Initialize rate limiter (using Redis)
    import aioredis
    redis = await aioredis.create_redis_pool("redis://localhost")
    await FastAPILimiter.init(redis)

@app.post("/profile", dependencies=[Depends(get_current_user)])
def get_profile(user=Depends(get_current_user)):
    AUDIT_LOG.append({"user": user["sub"], "action": "view_profile", "timestamp": datetime.utcnow().isoformat()})
    return {"username": user["sub"], "role": user["role"]}

@app.post("/password-reset-request")
def password_reset_request(username: str = Body(...), background_tasks: BackgroundTasks = None):
    if username not in USER_DB:
        return {"error": "User not found"}
    token = str(uuid.uuid4())
    PASSWORD_RESET[username] = token
    # Simulate sending email
    if background_tasks:
        background_tasks.add_task(print, f"Send password reset email to {username} with token {token}")
    AUDIT_LOG.append({"user": username, "action": "password_reset_requested", "timestamp": datetime.utcnow().isoformat()})
    return {"msg": "Password reset email sent"}

@app.post("/password-reset")
def password_reset(username: str = Body(...), token: str = Body(...), new_password: str = Body(...)):
    if PASSWORD_RESET.get(username) != token:
        return {"error": "Invalid token"}
    USER_DB[username]["password"] = pwd_context.hash(bcrypt_safe(new_password))
    AUDIT_LOG.append({"user": username, "action": "password_reset", "timestamp": datetime.utcnow().isoformat()})
    return {"msg": "Password updated"}

@app.post("/verify-email")
def verify_email(username: str = Body(...), background_tasks: BackgroundTasks = None):
    if username not in USER_DB:
        return {"error": "User not found"}
    token = str(uuid.uuid4())
    EMAIL_VERIFICATION[username] = token
    if background_tasks:
        background_tasks.add_task(print, f"Send verification email to {username} with token {token}")
    AUDIT_LOG.append({"user": username, "action": "email_verification_requested", "timestamp": datetime.utcnow().isoformat()})
    return {"msg": "Verification email sent"}

@app.post("/confirm-email")
def confirm_email(username: str = Body(...), token: str = Body(...)):
    if EMAIL_VERIFICATION.get(username) != token:
        return {"error": "Invalid token"}
    USER_DB[username]["verified"] = True
    AUDIT_LOG.append({"user": username, "action": "email_verified", "timestamp": datetime.utcnow().isoformat()})
    return {"msg": "Email verified"}


@app.get("/audit-log", dependencies=[Depends(require_role("admin"))])
def get_audit_log():
    return AUDIT_LOG


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
