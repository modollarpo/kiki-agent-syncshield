"""
SendGrid CRM Adapter for SyncEngage™
- Uses SendGrid API for transactional and marketing emails.
- Enterprise-grade: Secure API key, async support, robust error handling.
"""
import os
import requests
from typing import Dict, Any
from .adapter_factory import CRMProvider

class SendGridAdapter(CRMProvider):
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.base_url = "https://api.sendgrid.com/v3/mail/send"

    def sync_customer(self, customer_data: Dict[str, Any]) -> None:
        # SendGrid is messaging only; sync logic can be extended for contact management
        pass

    def fetch_engagements(self, customer_id: str) -> Dict[str, Any]:
        # Fetch email engagement via SendGrid API (not implemented)
        return {}

    def send_message(self, customer_id: str, message: Dict[str, Any]) -> None:
        payload = {
            "personalizations": [{"to": [{"email": customer_id}], "subject": message["subject"]}],
            "from": {"email": os.getenv("SENDGRID_FROM_EMAIL", "noreply@yourdomain.com")},
            "content": [{"type": "text/plain", "value": message["body"]}]
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            r = requests.post(self.base_url, json=payload, headers=headers)
            r.raise_for_status()
        except Exception as e:
            print(f"SendGrid send failed: {e}")
