# KIKI Agent™ Architecture

## Overview

KIKI Agent™ is a modular, microservices-based autonomous revenue engine. Each service is independently deployable and communicates via gRPC and REST APIs. The system is designed for high performance, scalability, and compliance.

## Service Map

- **SyncBrain**: LLM Orchestration

- **SyncValue**: LTV Prediction
- **SyncFlow**: Real-time Bidding
- **SyncCreate**: Creative Generation
- **SyncEngage**: CRM Automation
- **SyncShield**: Compliance & Audit

## Infrastructure

- API Gateway (Kong/Traefik)

- Service Mesh (Istio/Linkerd)
- PostgreSQL, Redis, MinIO/S3
- Kubernetes, Docker

See `/docs/AGENT_SPEC.md` for agent details.
