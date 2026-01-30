# LLM Template Engine for Explainability Broker
from typing import Dict

def render_client_notification(event: Dict) -> str:
    return (
        f"KIKI detected a {event.get('observation', 'market change')}. "
        f"{event.get('agent', 'An agent')} just {event.get('action', 'took action')}. "
        f"Estimated ROI: {event.get('financial_impact', {}).get('estimated_roi', 'N/A')}{event.get('financial_impact', {}).get('currency', '')}."
    )

def render_admin_notification(event: Dict) -> str:
    details = event.get('technical_details', {})
    threshold_info = (
        f" (threshold: {details.get('threshold')})" if 'threshold' in details else ""
    )
    return (
        f"{event.get('agent', 'Agent')} intercepted an event. Reason: {event.get('reasoning', 'N/A')}{threshold_info}. "
        f"Action: {event.get('action', 'N/A')}. Recovery: {event.get('recovery_path', 'N/A')}."
    )

# Example usage:
if __name__ == "__main__":
    client_event = {
        "observation": "22% spike in 'Tech Enthusiast' engagement",
        "agent": "SyncCreate",
        "action": "generated 3 cinematic videos for LinkedIn",
        "financial_impact": {"estimated_roi": 14, "currency": "%"}
    }
    admin_event = {
        "agent": "SyncShield",
        "reasoning": "Brand Safety Score fell below 0.85 (detected distorted logo)",
        "action": "Automated rollback triggered",
        "recovery_path": "Stable Asset #402 deployed",
        "technical_details": {"brand_safety_score": 0.82, "threshold": 0.85}
    }
    print("Client:", render_client_notification(client_event))
    print("Admin:", render_admin_notification(admin_event))
