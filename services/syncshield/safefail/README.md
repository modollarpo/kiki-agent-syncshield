# SafeFailGuard (SyncShield)


**Purpose:**

- Monitors SyncReflex feedback for sudden drops in performance or spikes in negative sentiment.
- Automatically triggers rollbacks of AI-generated ads or bidding strategies if thresholds are breached.
- Exposes REST endpoints for manual override and status.



**Endpoints:**

- `POST /safefail/trigger` — Manually trigger a rollback.
- `GET /safefail/status` — Get current thresholds and last score.



**Integration:**

- Polls or subscribes to SyncReflex feedback (gRPC/REST).
- Calls rollback logic in SyncFlow, SyncCreate, etc.
- Logs all events for compliance/audit.



**Next Steps:**

- Wire up real SyncReflex feedback (replace mock).
- Integrate with rollback APIs in other agents.
- Add audit logging and notification hooks.

