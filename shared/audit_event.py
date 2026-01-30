from typing import Dict, Any

class AuditEvent:
    def __init__(self, event: str, user_id: str, data: Dict[str, Any]):
        self.event = event
        self.user_id = user_id
        self.data = data
