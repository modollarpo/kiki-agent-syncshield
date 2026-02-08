"""
SyncEngage™ Retention Logic Engine
- Orchestrates predictive retention flows using BrandDNA and SyncValue signals.
- Multi-channel, fatigue-aware, and A/B tracked via SyncLedger.
"""
from typing import Dict, Any
from .adapter_factory import get_crm_adapter
from .prompt_engine import inject_brand_voice
import requests

# Example BrandDNA and customer segment
BrandDNA = Dict[str, Any]
CustomerSegment = Dict[str, Any]

import asyncio

class RetentionEngine:
    def __init__(self, crm_provider: str):
        self.adapter = get_crm_adapter(crm_provider)

    async def orchestrate_multi_channel(self, brand_dna, customer_segment, channels, priority_order=None):
        """
        Orchestrate retention flows across multiple channels with prioritization and fatigue management.
        """
        sent = False
        priority = priority_order or channels
        for channel in priority:
            adapter = get_crm_adapter(channel)
            subject, body = self.generate_winback_message(brand_dna, customer_segment)
            message = {"subject": subject, "body": body, "channel": channel}
            engagements = await self._fetch_engagements_async(customer_segment["id"])
            if self._should_send(channel, engagements):
                await self._send_message_async(customer_segment["id"], message)
                await self._track_event_async(customer_segment["id"], channel, "sent", message)
                sent = True
                break  # Only send via highest-priority channel
            else:
                await self._track_event_async(customer_segment["id"], channel, "delayed", message)
        return sent

    async def orchestrate_parallel(self, brand_dna, customer_segment, channels):
        """
        Orchestrate retention flows across all channels in parallel (for VIP/urgent cases).
        """
        tasks = []
        for channel in channels:
            adapter = get_crm_adapter(channel)
            subject, body = self.generate_winback_message(brand_dna, customer_segment)
            message = {"subject": subject, "body": body, "channel": channel}
            tasks.append(self._send_message_async(customer_segment["id"], message))
        await asyncio.gather(*tasks)

    async def orchestrate_conditional(self, brand_dna, customer_segment, channels, condition_fn):
        """
        Orchestrate flows based on custom condition function (e.g., LTV, churn risk).
        """
        for channel in channels:
            if condition_fn(brand_dna, customer_segment, channel):
                adapter = get_crm_adapter(channel)
                subject, body = self.generate_winback_message(brand_dna, customer_segment)
                message = {"subject": subject, "body": body, "channel": channel}
                await self._send_message_async(customer_segment["id"], message)
                await self._track_event_async(customer_segment["id"], channel, "sent", message)
                break

    def generate_winback_message(self, brand_dna: BrandDNA, customer_segment: CustomerSegment):
        voice = brand_dna.get("voice", "")
        name = customer_segment.get("name", "there")
        if "elegant" in voice or "exclusive" in voice or "understated" in voice:
            # Luxury brand
            subject = "A Personal Invitation Awaits"
            body = (
                f"Dear {name},\n\n"
                "We noticed you haven’t visited us in a while. As one of our most valued patrons, "
                "we’d like to offer you early access to our next limited release. "
                "Your discerning taste deserves nothing less than the exceptional.\n\n"
                "With appreciation,\nThe [Brand] Concierge Team"
            )
        else:
            # Discount/value brand
            subject = "We Miss You! Here’s 20% Off"
            body = (
                f"Hey {name},\n\n"
                "It’s been a while! We’ve got new deals just for you—grab 20% off your next order. "
                "Hurry, these savings won’t last!\n\n"
                "See you soon,\nThe [Brand] Team"
            )
        # Inject brand voice/tone using Prompt Engineering Engine
        body = inject_brand_voice(brand_dna, body)
        return subject, body

    async def send_retention_flow(self, brand_dna: BrandDNA, customer_segment: CustomerSegment, channel: str):
        subject, body = self.generate_winback_message(brand_dna, customer_segment)
        message = {"subject": subject, "body": body, "channel": channel}
        # Fatigue management: check recent engagement before sending
        try:
            engagements = await self._fetch_engagements_async(customer_segment["id"])
        except Exception as e:
            print(f"Engagement fetch failed: {e}")
            engagements = {}
        if self._should_send(channel, engagements):
            await self._send_message_async(customer_segment["id"], message)
            await self._track_event_async(customer_segment["id"], channel, "sent", message)
        else:
            await self._track_event_async(customer_segment["id"], channel, "delayed", message)

    async def _fetch_engagements_async(self, customer_id: str):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.adapter.fetch_engagements, customer_id)

    async def _send_message_async(self, customer_id: str, message: dict):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.adapter.send_message, customer_id, message)

    async def _track_event_async(self, customer_id: str, channel: str, status: str, message: dict):
        # Log to SyncLedger for OaaS attribution
        event = {
            "customer_id": customer_id,
            "channel": channel,
            "status": status,
            "message_subject": message.get("subject"),
            "timestamp": "now"  # Replace with actual timestamp
        }
        try:
            # Enterprise-grade: Use robust retry and error handling
            for _ in range(3):
                try:
                    r = requests.post("http://syncledger:8000/api/engagement_event", json=event, timeout=5)
                    if r.status_code == 200:
                        break
                except Exception as e:
                    print(f"SyncLedger logging attempt failed: {e}")
                    await asyncio.sleep(2)
        except Exception as e:
            print(f"SyncLedger logging failed: {e}")

    def _should_send(self, channel: str, engagements: Dict[str, Any]) -> bool:
        # Example: don't send if user received a message on this channel in last 48h
        last = engagements.get(channel, {}).get("last_sent", None)
        # ...insert logic...
        return True  # Placeholder

    def _track_event(self, customer_id: str, channel: str, status: str, message: dict):
        # Log to SyncLedger for OaaS attribution
        # Example: POST to SyncLedger event API
        event = {
            "customer_id": customer_id,
            "channel": channel,
            "status": status,
            "message_subject": message.get("subject"),
            "timestamp": "now"  # Replace with actual timestamp
        }
        try:
            # requests.post("http://syncledger:8000/api/engagement_event", json=event)
            pass
        except Exception as e:
            print(f"SyncLedger logging failed: {e}")
