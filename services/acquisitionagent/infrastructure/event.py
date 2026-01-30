"""
Event-driven output adapter
- Abstracts event publishing (e.g., Kafka, Pub/Sub)
- All external systems are mocked
"""
def publish_event(event: str):
    """
    Publish an event to the event bus (stubbed)
    """
    # In production, this would publish to Kafka, Pub/Sub, etc.
    # Here, we just log or collect events for testing
    print(f"Event published: {event}")
