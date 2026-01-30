
# KIKI Agent™ – Copilot AI Coding Instructions

Act as a Staff Systems Architect. We are building the KIKI Agent™ platform using Clean Architecture and Domain-Driven Design (DDD). Before writing code, you must initialize the workspace structure. We will proceed service-by-service. Acknowledge this by presenting a high-level System Design Document and the Shared Proto Definitions for cross-service communication.

## System Overview
KIKI Agent™ is a multi-service, microservices-based autonomous revenue engine. Each service is independently deployable, communicates via REST/gRPC, and is orchestrated through an API gateway and service mesh. The system is designed for high performance, scalability, and compliance.

## Key Services & Patterns
- **SyncBrain**: Python/FastAPI, LLM orchestration, OpenAI integration, context management, rules/guardrails. Calls other agents via service mesh.
- **SyncValue**: Python, PyTorch, dRNN, zero-shot learning, full LTV pipeline. APIs for prediction, training, metrics.
- **SyncFlow**: Go, Gin, <1ms real-time bidding, WebSocket/gRPC adapters, rules engine, ad network adapters.
- **SyncCreate**: Python, Stable Diffusion, creative generation, brand-safety classifier.
- **SyncEngage**: Python (or Node.js), CRM automation, churn/upsell triggers.
- **SyncShield**: Go, compliance, audit logging, AES-256 encryption, data minimization.

## Infrastructure
- All services have Dockerfiles and are orchestrated via docker-compose and Kubernetes manifests in `/deploy`.
- API Gateway (Python FastAPI, placeholder for Kong/Traefik) proxies requests to services.
- Service mesh (Istio/Linkerd) and gRPC for internal agent communication.
- PostgreSQL, Redis, MinIO/S3 for data/model storage.

## Developer Workflows
- **Build/Run**: Use `docker-compose up` for local dev. For Kubernetes, apply manifests in `/deploy`.
- **Testing**: Each service has a `/tests` folder with unit/integration tests. Use pytest (Python), Go test, or Jest as appropriate.
- **API**: All APIs are RESTful, with OpenAPI schemas where possible. See `/openapi/openapi.yaml` and `/docs/API_REFERENCE.md`.
- **CI/CD**: GitHub Actions workflows and Terraform scripts are in `/deploy`.

## Conventions
- Strong typing (Python typing, Go structs, TypeScript).
- Docstrings and comments required for all modules and functions.
- Health checks at `/healthz` for all services.
- Use `/shared`, `/schemas`, `/utils`, `/types`, `/constants` for cross-service code and definitions.
- All external service calls should be mocked in tests.

## Examples
- See `/services/syncbrain/app/main.py` for FastAPI patterns and context management.
- See `/services/syncvalue/app/ltv_dRNN.py` for model structure.
- See `/services/syncflow/app/main.go` for high-performance Go API.

## Integration Points
- Internal service calls use gRPC or REST via the service mesh.
- API Gateway aggregates and authenticates all external traffic.
- Adapters for Meta/Google APIs are in SyncFlow.
- CRM integrations are in SyncEngage.

## Monitoring & Compliance
- Prometheus/Grafana for monitoring (add exporters as needed).
- SyncShield logs all compliance/audit events.

---
For more details, see `/docs/ARCHITECTURE.md` and `/docs/AGENT_SPEC.md`.
