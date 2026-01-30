import time
import json
import os

def stream_audit_log(log_path, poll_interval=2):
    """Stream new lines from the audit log in real time."""
    if not os.path.exists(log_path):
        print(f"Log file {log_path} does not exist.")
        return
    with open(log_path, 'r') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(poll_interval)
                continue
            try:
                event = json.loads(line)
                print(f"[{event['timestamp']}] {event['action']} | Reason: {event['reasoning_code']} | Revenue: ${event['ai_revenue']}")
            except Exception:
                print(line.strip())

if __name__ == "__main__":
    log_path = os.path.join(os.path.dirname(__file__), '../../logs/syncshield/audit.json')
    stream_audit_log(os.path.abspath(log_path))
