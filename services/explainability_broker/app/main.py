from fastapi import FastAPI, APIRouter
from translator_logic import explainability_translate
from syncshield_grpc_client import SyncShieldAuditLogClient
from typing import List

app = FastAPI(title="Explainability Broker")
router = APIRouter()

# Instantiate the real SyncShield gRPC client
syncshield_client = SyncShieldAuditLogClient()

@router.get("/api/v1/explainability/feed")
async def explainability_feed():
    # Fetch recent audit logs from SyncShield via gRPC
    logs = syncshield_client.get_recent_logs()
    # Convert logs to explainable narratives
    narratives = [explainability_translate({
        'time': log['metadata'].get('timestamp'),
        'agent': log['agent_id'],
        'action': log['action_type'],
        'meta': log['metadata']
    }) for log in logs]
    return narratives

app.include_router(router)
