CHANNELS = {
    "client": [
        {"type": "slack", "webhook": "https://hooks.slack.com/services/your/client/webhook"},
        {"type": "email", "address": "client@example.com"}
    ],
    "admin": [
        {"type": "slack", "webhook": "https://hooks.slack.com/services/your/admin/webhook"},
        {"type": "pagerduty", "integration_key": "your-pagerduty-key"}
    ],
    "compliance": [
        {"type": "email", "address": "compliance@example.com"}
    ]
}

FILTERS = {
    "client": lambda event: event.get("financial_impact", {}).get("estimated_roi", 0) > 0,
    "admin": lambda event: event.get("agent", "").startswith("SyncShield") or event.get("reasoning", "").lower().find("fail") != -1,
    "compliance": lambda event: event.get("action", "").lower().find("rollback") != -1
}

LLM_PROVIDERS = {
    "openai": {"module": "llm_api", "function": "generate_business_narrative"},
    "anthropic": {"module": "llm_anthropic", "function": "generate_narrative"}
}
