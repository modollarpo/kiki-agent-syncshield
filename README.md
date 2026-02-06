# KIKI Agent™ Platform

KIKI Agent™ is a next-generation, cloud-native, autonomous revenue engine designed for digital businesses that demand high performance, scalability, and compliance. The platform leverages a microservices architecture, orchestrating a suite of intelligent agents—each responsible for a specialized business function—using Clean Architecture and Domain-Driven Design (DDD) principles.

## Platform Overview

KIKI Agent™ is built for modularity and extensibility, enabling organizations to deploy, scale, and evolve their digital operations with ease. Each agent is independently deployable, communicates via REST/gRPC, and is orchestrated through a secure API gateway and service mesh. The system is designed for seamless integration with cloud infrastructure, supporting rapid innovation and robust compliance.

## Core Agents and Services

- **SyncBrain:** LLM orchestration, OpenAI integration, context management, and rules/guardrails.
- **SyncValue:** Lifetime value (LTV) prediction, dRNN, zero-shot learning, and full LTV pipeline.
- **SyncFlow:** Real-time bidding engine (<1ms), WebSocket/gRPC adapters, rules engine, and ad network adapters.
- **SyncCreate:** Creative generation using Stable Diffusion, brand-safety classifier.
- **SyncEngage:** CRM automation, churn/upsell triggers, customer engagement workflows.
- **SyncShield:** Compliance, audit logging, AES-256 encryption, data minimization, and safe-fail mechanisms.
- **SyncBill:** Automated billing, invoicing, and financial reconciliation.
- **SyncNotify:** Notification and alerting system for internal and external events.
- **SyncPortal:** User and partner portal for management and analytics.
- **SyncMultimodal:** Multimodal data processing and analytics.
- **SyncTwin:** Digital twin modeling and simulation.
- **SyncReflex:** Real-time feedback and adaptive control.
- **AcquisitionAgent:** User acquisition and growth automation.
- **ExplainabilityBroker:** Model explainability, transparency, and compliance reporting.
- **Dashboard:** Centralized UI for monitoring, analytics, and agent management.

## Key Features

- **Microservices & Service Mesh:** Each agent is a microservice, enabling independent scaling, deployment, and updates.
- **Cloud-Native:** Optimized for Azure AKS, with full CI/CD automation via GitHub Actions.
- **Cross-Language:** Services implemented in Python, Go, and TypeScript.
- **Secure & Compliant:** Built-in audit logging, encryption, and compliance guardrails.
- **Observability:** Integrated with Prometheus and Grafana for monitoring and alerting.
- **Extensible:** Easily add new agents or integrations for ad networks, CRM, analytics, and more.
- **🚀 URL-to-Campaign Automation:** Transform any website URL into a complete, deployed advertising campaign with KIKI's "Advantage+ Suite" - see [URL_TO_CAMPAIGN.md](docs/URL_TO_CAMPAIGN.md)

## 🚀 Council of Nine: Two Entry Points for Campaign Automation

KIKI's flagship orchestration feature - the "Council of Nine" - coordinates all KIKI agents to transform your input into a complete, deployed advertising campaign. Users can interact with KIKI through **two primary entry points**:

### 1. **Prompt-to-Campaign** (⭐ PRIMARY)

Transform natural language prompts into complete campaigns - no website required.

```bash
# Example: Budget + ROI constraint
curl -X POST http://localhost:8002/api/v1/prompt-to-campaign \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Launch product with $100k budget, target ROI 3x"}'

# Example: Industry + audience targeting
curl -X POST http://localhost:8002/api/v1/prompt-to-campaign \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create campaign for SaaS startup, B2B enterprise audience, $50k budget"}'

# Auto-deploy mode
curl -X POST http://localhost:8002/api/v1/prompt-to-campaign \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Mobile game launch, casual players, $25k budget", "auto_deploy": true}'
```

**What it does**:
- Parses natural language → Extracts budget, ROI, industry, audience
- Predicts LTV baseline → Calculates max CPA from ROI target
- Generates 5 ad copies + 3 image prompts
- Validates brand safety
- Deploys with budget & ROI constraints

**Example Script**: `python services/syncvalue/example_prompt_to_campaign.py`

---

### 2. **URL-to-Campaign**

Transform an existing website into a campaign by extracting brand identity.

```bash
# Extract brand from URL and generate campaign
curl -X POST http://localhost:8002/api/v1/url-to-campaign \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "auto_deploy": true}'
```

**What it does**:
- Scrapes URL → Extracts brand identity, colors, tone
- Classifies industry (E-commerce, SaaS, Gaming, etc.)
- Predicts LTV baseline ($60-$2500+)
- Generates on-brand ad creatives
- Deploys with LTV constraints

**Example Script**: `python services/syncvalue/example_url_to_campaign.py`

---

### The Advantage+ Suite

KIKI enhances Meta's core automation features with LTV-based intelligence:

| Meta Feature | KIKI Enhancement |
|--------------|------------------|
| **Advantage+ Audience** | **SyncValue™ + SyncBrain™**: LTV-based targeting, not just CPA |
| **Advantage+ Creative** | **SyncCreate™ + SyncShield™**: Autonomous generation with brand safety |
| **Advantage+ Placements** | **SyncFlow™**: LTV-optimized bidding with <1ms real-time execution |

**Complete Documentation**: [URL_TO_CAMPAIGN.md](docs/URL_TO_CAMPAIGN.md)

## Technologies

- Azure AKS, Azure Container Registry, Kubernetes, Docker
- FastAPI, Gin (Go), Next.js, PyTorch, Stable Diffusion
- PostgreSQL, Redis, MinIO/S3
- gRPC, REST, OpenAPI

## Documentation

- See `/docs/ARCHITECTURE.md` for system design and architecture.
- See `/docs/API_REFERENCE.md` for API details.
- See `/docs/AGENT_SPEC.md` for agent roles, protocols, and integration patterns.

## Local Development (Docker Compose)

Prereqs:

- A working Docker daemon (Docker Desktop, Rancher Desktop, etc.). The VS Code Docker extension is a UI on top of the daemon; it can’t run containers by itself.
- Repo root `.env` populated (this repo includes a root `.env.example` you can copy from).

### VS Code: Docker Extension (`ms-azuretools.vscode-docker`)

1) Start Docker Desktop and wait for it to report “Running”.
2) Open this repo root in VS Code.
3) In the **Docker** side panel, confirm you can see **Containers** / **Images** (if it shows “cannot connect”, the daemon isn’t running).
4) Right-click `docker-compose.yml` → **Compose Up** (or Command Palette → “Docker: Compose Up”).
	- Note: `traefik` is behind the optional `edge` profile. Bring it up only when needed.
5) Verify the gateway:

- `http://localhost:8080/healthz`
- `http://localhost:8080/health/services` (uses `INTERNAL_API_KEY` if set)

### Required environment values

For a clean local compose run (no missing-var warnings), set at least:

- `INTERNAL_API_KEY`
- `JWT_SECRET`
- `JWT_ALGORITHM` (default `HS256`)
- `CORS_ALLOW_ORIGINS` (e.g. `http://localhost:3001` for the dashboard)

### Optional: enable Traefik (edge profile)

- CLI: `docker compose --profile edge up -d --build`
- Or set `COMPOSE_PROFILES=edge` in your environment before running Compose.

This repository contains the full production-grade, multi-service architecture for the KIKI Agent™ Autonomous Revenue Engine. Each service is isolated, scalable, and designed for enterprise deployment.

## Services

- **SyncBrain**: LLM Orchestration (FastAPI + Python)
- **SyncValue**: LTV Prediction Engine (Python + PyTorch)
- **SyncFlow**: Real-time Bidding Engine (GoLang)
- **SyncCreate**: Creative Generation (Python, Stable Diffusion)
- **SyncEngage**: CRM + Retention Automation (Node.js or Python)
- **SyncShield**: Compliance + Audit Logging (GoLang)

## Infrastructure

- Docker, Kubernetes, API Gateway, Service Mesh, PostgreSQL, Redis, MinIO/S3

See `/docs` for full architecture and API documentation.
