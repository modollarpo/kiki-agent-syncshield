# Explainability Broker Service

This microservice provides the event-driven Explainability Bus for the Council of Nine platform.


## Features

- Accepts explainability notifications (JSON or Protobuf) from all agents
- Publishes events to Redis stream `kiki:explainability:events`
- REST API for posting and retrieving explainability events
- Ready for integration with LLM template engine and notification system



## API

- `POST /notify` — Accepts an ExplainabilityNotification payload
- `GET /events` — Returns the last 10 explainability events



## Usage

1. Start Redis locally (or use Docker)
2. Run the broker: `python main.py`
3. Agents POST to `/notify` with explainability payloads
4. Downstream services (UI, notification, audit) consume from Redis stream



## Codegen

- Use `schemas/explainability_notification.proto` for gRPC/Protobuf codegen
- Use `schemas/explainability_notification.schema.json` for JSON validation. For API schema, see `/openapi/openapi.yaml`.



## Example

```bash
curl -X POST http://localhost:8089/notify \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt-20260126-001",
    "timestamp": "2026-01-26T12:00:00Z",
    "agent": "SyncCreate",
    "recipient_type": "client",
    "reasoning": "Detected 22% spike in Tech Enthusiast engagement.",
    "action": "Generated 3 cinematic videos for LinkedIn."
  }'
```
