import redis
import json

class ExplainabilityEventBus:
    def __init__(self, host='localhost', port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db)

    def publish(self, event: dict):
        self.r.xadd('kiki:explainability:events', event)

    def subscribe(self, count=10):
        # Returns the last N events
        events = self.r.xrevrange('kiki:explainability:events', count=count)
        return [dict(e[1]) for e in events]

# Example usage:
if __name__ == "__main__":
    bus = ExplainabilityEventBus()
    bus.publish({"event_id": "evt-1", "agent": "SyncBrain", "reasoning": "Test"})
    print(bus.subscribe())
