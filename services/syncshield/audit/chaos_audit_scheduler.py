import subprocess
import time
from datetime import datetime
import schedule

def run_stealth_chaos_test():
    # 1. Inject latency to SyncFlow
    subprocess.run([
        "docker", "exec", "kiki-syncflow-1", "tc", "qdisc", "add", "dev", "eth0", "root", "netem", "delay", "200ms"
    ], check=False)
    # 2. Trigger market crash
    subprocess.run([
        "curl", "-X", "POST", "http://localhost:8080/syncreflex/simulate-crash",
        "-d", '{"drop_percentage": 10, "event_type": "STEALTH_AUDIT"}'
    ], check=False)
    print(f"[Stealth Chaos Test] Injected at {datetime.now()}")
    # Wait for system to respond, then heal
    time.sleep(10)
    subprocess.run([
        "docker", "exec", "kiki-syncflow-1", "tc", "qdisc", "del", "dev", "eth0", "root", "netem"
    ], check=False)
    subprocess.run([
        "curl", "-X", "POST", "http://localhost:8080/syncreflex/signal-recovery"
    ], check=False)
    print(f"[Stealth Chaos Test] Healed at {datetime.now()}")
    # Trigger chaos report generation
    subprocess.run([
        "python", "generate_chaos_report.py"
    ], check=False)

def schedule_weekly_audit():
    # Schedule for Sunday at 2:00 AM
    schedule.every().sunday.at("02:00").do(run_stealth_chaos_test)
    print("[Scheduler] Weekly Stealth Audit scheduled for Sundays at 2:00 AM.")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    schedule_weekly_audit()
