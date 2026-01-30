import requests

def send_slack_notification(webhook_url, message):
    resp = requests.post(webhook_url, json={"text": message}, timeout=10)
    resp.raise_for_status()
    print("[Slack] Notification sent.")

def send_teams_notification(webhook_url, message):
    payload = {"text": message}
    resp = requests.post(webhook_url, json=payload, timeout=10)
    resp.raise_for_status()
    print("[Teams] Notification sent.")

def send_pagerduty_event(routing_key, summary, severity="info"):
    url = "https://events.pagerduty.com/v2/enqueue"
    payload = {
        "routing_key": routing_key,
        "event_action": "trigger",
        "payload": {
            "summary": summary,
            "severity": severity,
            "source": "kiki-chaos-audit",
            "component": "syncshield"
        }
    }
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    print("[PagerDuty] Event triggered.")
