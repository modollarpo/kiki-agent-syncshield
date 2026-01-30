# SyncBrain Service

Python microservice for LLM orchestration, context management, and strategy logic.

- Clean Architecture: domain, usecase, adapter, infra
- Entry: main.py# SyncBrain – LLM Orchestration Service

- FastAPI, Python
- Orchestrates LLM-based strategies
- Endpoints: /plan-strategy, /coordinate-agents, /evaluate-performance
- Integrates with OpenAI/Azure OpenAI
- Calls other agents via service mesh
