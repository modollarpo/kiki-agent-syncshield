# KIKI Agent™ Owner's Manual: SyncShield Safe-Fail & Rollback Module

## Disaster Recovery Protocols

- **Automatic Rollback:** If SyncReflex detects >20% CTR drop, SyncShield triggers rollback to stable asset.
- **Circuit Breaker:** SyncFlow pivots to Conservative Bidding if risk flagged.
- **Stable State Cache:** Proven Gold assets are deployed as emergency fallback.
- **Sentiment Scrutiny:** All generated content is scanned for negative/off-brand sentiment before release.

## Master Override Codes

- **Emergency Revert:** Manual trigger available in Guardian Dashboard ('Human Review Required').
- **Override API:** Secure endpoint for authorized override actions (see /services/syncshield/logic/safefail.go).
- **Audit Logging:** All interventions logged for compliance and traceability.

## Tuning AI Risk Appetite

- **MaxDriftThreshold:** Set in RollbackManager (default: 0.20). Lower for more conservative, raise for aggressive.
- **Sentiment Guard:** Adjust NLP model sensitivity for brand safety.
- **Performance Thresholds:** Configure via dashboard or config file for campaign-specific risk profiles.

## Emergency UI: Guardian Dashboard

| Metric            | Description                                 | Visual Element         |
|-------------------|-----------------------------------|----------------------|
| Bids Blocked      | High-risk bids stopped by SyncShield | Red Counter          |
| Auto-Rollbacks    | System reverted to stable state    | Circular Progress    |
| Sentiment Guard   | Real-time "Safety Score" of Council of Nine | Pulse Line (Color)   |
| Human Review Req. | Manual override/intervention required | Button/Alert         |

## Disaster Recovery Steps

1. **Detection:** SyncReflex/SyncShield monitor for anomalies.
2. **Interception:** Circuit breaker halts risky actions.
3. **Rollback:** Stable asset deployed, risky campaign paused.
4. **Notification:** Human-in-the-Loop alerted via dashboard and Slack.
5. **Audit:** All actions logged for review and compliance.

## Scaling Guidance

- **Increase MaxDriftThreshold** for higher risk tolerance as budget grows.
- **Expand Stable State Library** with new high-performing assets.
- **Integrate additional toolchains** (Sentry, Datadog, Prometheus) for deeper observability.
- **Regularly review audit logs** and prevention metrics to tune system.

---

For full technical details, see:
- /services/syncshield/logic/safefail.go


- /services/syncshield/logic/safefail_test.go
- /deploy/charts/syncshield-safefail/
- /docs/ARCHITECTURE.md
- /docs/AGENT_SPEC.md

---

**Council of Nine is now invincible.**
