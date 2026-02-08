from fastapi import FastAPI, APIRouter
from translator_logic import explainability_translate
from syncshield_grpc_client import SyncShieldAuditLogClient
from typing import List






































    return JSONResponse(content=narratives)    narratives = [translate_log(log['agent_id'], log['action_type'], log['metadata']) for log in logs]    logs = get_recent_agent_logs()def explainability_feed():@app.get("/api/v1/explainability/feed")    ]        },            'metadata': {'amount': 2000, 'from_platform': 'Google', 'to_platform': 'TikTok', 'cpa_delta': 30, 'timestamp': '2026-02-08T12:00:00Z'}            'action_type': 'pivot',            'agent_id': 'SyncBrain',        {        },            'metadata': {'revenue_lift': 18, 'confidence': 92, 'timestamp': '2026-02-08T11:00:00Z'}            'action_type': 'simulation',            'agent_id': 'SyncTwin',        {        },            'metadata': {'creative_id': 4, 'savings': 450, 'timestamp': '2026-02-08T10:03:00Z'}            'action_type': 'rollback',            'agent_id': 'SyncShield',        {        },            'metadata': {'platform': 'Meta', 'percent': 20, 'timestamp': '2026-02-08T09:15:00Z'}            'action_type': 'bid_increase',            'agent_id': 'SyncFlow',        {    return [    # Example technical logsdef get_recent_agent_logs() -> List[dict]:# Simulated gRPC log subscriber (replace with real gRPC stream)app = FastAPI(title="Explainability Broker")from translator_logic import translate_logfrom typing import Listfrom fastapi.responses import JSONResponsefrom typing import List

from fastapi import FastAPI, APIRouter
from typing import List
from translator_logic import explainability_translate
from syncshield_grpc_client import SyncShieldAuditLogClient

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
