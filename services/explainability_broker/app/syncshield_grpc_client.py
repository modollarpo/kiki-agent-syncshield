import grpc
from typing import List, Dict, Any
# from generated.syncshield_pb2_grpc import AuditLogServiceStub
# from generated.syncshield_pb2 import GetRecentLogsRequest

SYNC_SHIELD_GRPC_ADDR = 'syncshield:50051'

class SyncShieldAuditLogClient:
    def __init__(self, address=SYNC_SHIELD_GRPC_ADDR):
        self.channel = grpc.insecure_channel(address)
        # self.stub = AuditLogServiceStub(self.channel)

    def get_recent_logs(self) -> List[Dict[str, Any]]:
        # Replace with real gRPC call
        # response = self.stub.GetRecentLogs(GetRecentLogsRequest(limit=20))
        # return [dict(log) for log in response.logs]
        # Simulated logs for now
        return [
            {
                'agent_id': 'SyncFlow',
                'action_type': 'bid_increase',
                'metadata': {'platform': 'Meta', 'percent': 20, 'timestamp': '2026-02-08T09:15:00Z'}
            },
            {
                'agent_id': 'SyncShield',
                'action_type': 'rollback',
                'metadata': {'creative_id': 4, 'savings': 450, 'timestamp': '2026-02-08T10:03:00Z'}
            },
            {
                'agent_id': 'SyncTwin',
                'action_type': 'simulation',
                'metadata': {'revenue_lift': 18, 'confidence': 92, 'timestamp': '2026-02-08T11:00:00Z'}
            },
            {
                'agent_id': 'SyncBrain',
                'action_type': 'pivot',
                'metadata': {'amount': 2000, 'from_platform': 'Google', 'to_platform': 'TikTok', 'cpa_delta': 30, 'timestamp': '2026-02-08T12:00:00Z'}
            },
        ]
