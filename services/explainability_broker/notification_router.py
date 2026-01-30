import requests
from typing import Dict
from channel_config import CHANNELS, FILTERS, LLM_PROVIDERS
import importlib

class NotificationRouter:
    def __init__(self, llm_provider="openai"):
        self.llm_provider = llm_provider

    def route(self, event: Dict, message: str):
        recipient = event.get("recipient_type")
        # Advanced filtering
        if recipient in FILTERS and not FILTERS[recipient](event):
            return
        # Multi-channel routing
        for channel in CHANNELS.get(recipient, []):
            self.send(channel, message)

    def send(self, channel: Dict, message: str):
        if channel["type"] == "slack":
            requests.post(channel["webhook"], json={"text": message})
        elif channel["type"] == "email":
            # Placeholder: integrate with email service
            print(f"Email to {channel['address']}: {message}")
        elif channel["type"] == "pagerduty":
            # Placeholder: integrate with PagerDuty
            print(f"PagerDuty alert: {message}")

    def select_llm(self, event: Dict):
        provider = event.get("llm_provider", self.llm_provider)
        config = LLM_PROVIDERS.get(provider)
        if not config:
            raise ValueError(f"Unknown LLM provider: {provider}")
        module = importlib.import_module(config["module"])
        func = getattr(module, config["function"])
        return func
