import os
import requests
from typing import Dict

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

API_URL = "https://api.anthropic.com/v1/complete"


def generate_narrative(event: Dict) -> str:
    prompt = f"You are an explainable AI system. Given this event: {event}, generate a concise, human-readable explanation."
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "content-type": "application/json"
    }
    data = {
        "model": "claude-2",
        "prompt": prompt,
        "max_tokens_to_sample": 120
    }
    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json().get("completion", "")
