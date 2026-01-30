import requests
import datetime

# Simulate a sudden market crash event for the Council of Nine

def simulate_market_crash():
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    event = {
        "agent_id": "SyncReflex",
        "action_type": "MARKET_CRASH_DETECTED",
        "confidence_score": 0.99,
        "intent": "Protect all campaigns from rapid market downturn",
        "evidence": "Detected 35% drop in CTR and 40% spike in bid volatility across all segments",
        "reasoning_text": "Market crash detected. Pivoting to Fortress risk profile. All high-risk bids paused, stable assets deployed."
    }
    # Send to SyncNotify (XAI notification broker)
    resp = requests.post("http://localhost:8089/notify", json=event)
    print(f"Chaos event sent. Status: {resp.status_code}, Response: {resp.text}")

if __name__ == "__main__":
    simulate_market_crash()
