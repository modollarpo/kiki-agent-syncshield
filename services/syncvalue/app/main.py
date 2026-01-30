"""
SyncValue – LTV Prediction Engine API
"""

from fastapi import FastAPI, HTTPException, Response, Body, Depends, status, BackgroundTasks
from pydantic import BaseModel, Field, ValidationError
from typing import Any, Dict, Optional

import torch
import os
import logging
from ltv_dRNN import LTVdRNN
from feature_extractor import extract_features
from training_loop import train_model
from inference import predict as model_predict
from services.syncvalue.app.handlers_ltv import router as ltv_router
import threading
import grpc
from concurrent import futures
from shared.types.python.value import value_pb2_grpc, value_pb2
from services.syncvalue.internal.usecases.ltv_inference import predict_ltv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt, uuid
from datetime import datetime, timedelta
from fastapi_limiter import FastAPILimiter, RateLimiter
import aioredis

# Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# OpenTelemetry tracing
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


app = FastAPI(title="SyncValue LTV Prediction", description="LTV prediction with dRNN, PyTorch, and zero-shot learning.")

# Instrument FastAPI with OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
FastAPIInstrumentor.instrument_app(app)
span_processor = BatchSpanProcessor(ConsoleSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

# Prometheus metrics
REQUEST_COUNT = Counter("syncvalue_requests_total", "Total requests", ["endpoint", "method"])
ERROR_COUNT = Counter("syncvalue_errors_total", "Total errors", ["endpoint"])
LTV_PREDICTIONS = Counter("syncvalue_ltv_predictions_total", "Total LTV predictions")
REQUEST_LATENCY = Histogram("syncvalue_request_latency_seconds", "Request latency", ["endpoint"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("syncvalue")

# Model config (for demo)
MODEL_PATH = os.getenv("LTV_MODEL_PATH", "ltv_model.pt")
INPUT_SIZE = 10
HIDDEN_SIZE = 16
NUM_LAYERS = 2
OUTPUT_SIZE = 1

def load_model():
    model = LTVdRNN(INPUT_SIZE, HIDDEN_SIZE, NUM_LAYERS, OUTPUT_SIZE)
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    return model

class PredictRequest(BaseModel):
    user_id: str = Field(..., json_schema_extra={"example": "user_123"})
    features: Dict[str, Any] = Field(..., json_schema_extra={"example": {"f1": 0.5, "f2": 1.2}})

class PredictResponse(BaseModel):
    ltv: float = Field(..., json_schema_extra={"example": 123.45})
    user_id: str = Field(..., json_schema_extra={"example": "user_123"})

class TrainRequest(BaseModel):
    dataset_path: str = Field(..., json_schema_extra={"example": "/data/ltv.csv"})
    params: Dict[str, Any] = Field(default_factory=dict)

class TrainResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "training_started"})
    dataset: str = Field(..., json_schema_extra={"example": "/data/ltv.csv"})

class MetricsResponse(BaseModel):
    accuracy: float = Field(..., json_schema_extra={"example": 0.95})
    loss: float = Field(..., json_schema_extra={"example": 0.1})

@app.post("/predict-ltv", response_model=PredictResponse, responses={
    200: {"description": "LTV prediction", "content": {"application/json": {"example": {"ltv": 123.45, "user_id": "user_123"}}}},
    400: {"description": "Invalid input"},
    500: {"description": "Model error"}
})
def predict_ltv(req: PredictRequest):
    REQUEST_COUNT.labels(endpoint="/predict-ltv", method="POST").inc()
    with REQUEST_LATENCY.labels(endpoint="/predict-ltv").time():
        with tracer.start_as_current_span("predict_ltv"):
    try:
        # Validate features strictly before model logic
        if not isinstance(req.features, dict) or not req.features:
            ERROR_COUNT.labels(endpoint="/predict-ltv").inc()
            raise HTTPException(status_code=400, detail="Features must be a non-empty dict.")
        feats = extract_features(req.features)
        # Ensure features are a 2D tensor: (batch, seq_len, input_size)
        # For demo, treat as batch=1, seq_len=1, input_size=INPUT_SIZE
        feat_vec = list(feats.values())[:INPUT_SIZE] + [0.0]*(INPUT_SIZE - len(feats))
        x = torch.tensor([ [feat_vec] ], dtype=torch.float32)  # shape: (1,1,INPUT_SIZE)
        model = load_model()
        y_pred = model_predict(model, x)
        ltv = float(y_pred.item())
        logger.info(f"Predicted LTV for {req.user_id}: {ltv}")
        LTV_PREDICTIONS.inc()
        return {"ltv": ltv, "user_id": req.user_id}
    except HTTPException as he:
        logger.error(f"Validation error: {he.detail}")
        ERROR_COUNT.labels(endpoint="/predict-ltv").inc()
        raise
    except ValidationError as ve:
        logger.error(f"Validation error: {ve}")
        ERROR_COUNT.labels(endpoint="/predict-ltv").inc()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Model error: {e}")
        ERROR_COUNT.labels(endpoint="/predict-ltv").inc()
        raise HTTPException(status_code=500, detail="Model error.")

@app.post("/train", response_model=TrainResponse, responses={
    200: {"description": "Training started", "content": {"application/json": {"example": {"status": "training_started", "dataset": "/data/ltv.csv"}}}},
    400: {"description": "Invalid input"},
    500: {"description": "Training error"}
})
def train(req: TrainRequest):
    try:
        # TODO: Load dataset, run training loop, save model
        logger.info(f"Training started on {req.dataset_path}")
        return {"status": "training_started", "dataset": req.dataset_path}
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=500, detail="Training error.")


# Include the new LTV router
app.include_router(ltv_router)

# Prometheus /metrics endpoint
@app.get("/metrics")
def prometheus_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# gRPC server implementation
class LTVServiceServicer(value_pb2_grpc.LTVServiceServicer):
    def PredictLTV(self, request, context):
        ltv = predict_ltv(dict(request.features))
        return value_pb2.PredictLTVResponse(user_id=request.user_id, ltv=ltv)
    def TrainLTV(self, request, context):
        # TODO: Implement training logic
        return value_pb2.TrainLTVResponse(status="training started")

def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    value_pb2_grpc.add_LTVServiceServicer_to_server(LTVServiceServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()

@app.on_event("startup")
def start_grpc_server():
    threading.Thread(target=serve_grpc, daemon=True).start()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
USER_DB = {"admin": {"username": "admin", "password": pwd_context.hash("adminpass"), "role": "admin"}}
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
EMAIL_VERIFICATION = {}
PASSWORD_RESET = {}
AUDIT_LOG = []

@app.on_event("startup")
async def startup():
    redis = await aioredis.create_redis_pool("redis://localhost")
    await FastAPILimiter.init(redis)

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

@app.post("/register")
def register(username: str = Body(...), password: str = Body(...), role: str = Body("analyst")):
    if username in USER_DB:
        return {"error": "User already exists"}
    USER_DB[username] = {"username": username, "password": pwd_context.hash(password), "role": role}
    return {"msg": "User registered"}

@app.post("/login", dependencies=[RateLimiter(times=5, seconds=60)])
def login(username: str = Body(...), password: str = Body(...)):
    user = USER_DB.get(username)
    if not user or not pwd_context.verify(password, user["password"]):
        return {"error": "Invalid credentials"}
    access_token = jwt.encode({
        "sub": username,
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }, SECRET_KEY, algorithm=ALGORITHM)
    AUDIT_LOG.append({"user": username, "action": "login", "timestamp": datetime.utcnow().isoformat()})
    return {"access_token": access_token, "token_type": "bearer"}

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
    if background_tasks:
        background_tasks.add_task(print, f"Send password reset email to {username} with token {token}")
    AUDIT_LOG.append({"user": username, "action": "password_reset_requested", "timestamp": datetime.utcnow().isoformat()})
    return {"msg": "Password reset email sent"}

@app.post("/password-reset")
def password_reset(username: str = Body(...), token: str = Body(...), new_password: str = Body(...)):
    if PASSWORD_RESET.get(username) != token:
        return {"error": "Invalid token"}
    USER_DB[username]["password"] = pwd_context.hash(new_password)
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
