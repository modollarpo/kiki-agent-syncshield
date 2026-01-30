
from datetime import date
from metrics_utils import get_prometheus_metric, get_grafana_panel_image
from email_utils import send_pdf_report
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io


# === CONFIGURATION ===
PROM_URL = "http://localhost:9090"
GRAFANA_URL = "http://localhost:3000"
GRAFANA_API_KEY = "eyJrIjoiZ3JhZmFuYV9hcGlfa2V5X2V4YW1wbGUiLCJuIjoiY2hhb3NfcmVwb3J0IiwiaWQiOjF9"  # Example key, replace with your real key
DASHBOARD_UID = "kiki-chaos"
PANEL_IDS = [2, 3, 4, 5, 6]  # Expanded list of panel IDs for advanced monitoring
SMTP_SERVER = "smtp.mailgun.org"
SMTP_PORT = 465
SMTP_USER = "chaos-reports@yourdomain.com"
SMTP_PASS = "supersecurepassword"
TO_EMAIL = "ops-team@yourdomain.com"

import requests

def generate_chaos_report(metrics_log=None):
    # Pull real metrics
    impact_area = get_prometheus_metric(PROM_URL, 'sum by(service) (chaos_injected_events)') or 'N/A'
    shield_interventions = get_prometheus_metric(PROM_URL, 'sum(invalid_bid_blocked_total)') or 'N/A'
    avg_latency = get_prometheus_metric(PROM_URL, 'avg_over_time(syncflow_bid_latency_ms[5m])') or 'N/A'
    error_rate = get_prometheus_metric(PROM_URL, 'sum(rate(syncflow_errors_total[5m]))') or 'N/A'
    cpu_usage = get_prometheus_metric(PROM_URL, 'avg_over_time(process_cpu_seconds_total[5m])') or 'N/A'
    mem_usage = get_prometheus_metric(PROM_URL, 'avg_over_time(process_resident_memory_bytes[5m])') or 'N/A'
    queue_depth = get_prometheus_metric(PROM_URL, 'max_over_time(syncflow_bid_queue_depth[5m])') or 'N/A'
    grpc_error_rate = get_prometheus_metric(PROM_URL, 'sum(rate(grpc_server_handled_total{code!="OK"}[5m]))') or 'N/A'
    creative_risk_score = get_prometheus_metric(PROM_URL, 'avg_over_time(synccreate_risk_score[5m])') or 'N/A'

    # Get multiple Grafana panel images (last 1h)
    from_ts = int((date.today().toordinal() - 1) * 86400000)
    to_ts = int(date.today().toordinal() * 86400000)
    panel_imgs = []
    for pid in PANEL_IDS:
        try:
            img = get_grafana_panel_image(GRAFANA_URL, GRAFANA_API_KEY, pid, DASHBOARD_UID, from_ts, to_ts)
            panel_imgs.append(img)
        except Exception:
            panel_imgs.append(None)

    # Generate PDF
    pdf_path = f"reports/chaos_{date.today()}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 720, "KIKI Agent™ Chaos Test Report")
    c.setFont("Helvetica", 12)
    c.drawString(72, 700, f"Blast Radius: {impact_area}")
    c.drawString(72, 680, f"Bids Blocked: {shield_interventions}")
    c.drawString(72, 660, f"Avg Bid Latency (ms): {avg_latency}")
    c.drawString(72, 640, f"SyncFlow Error Rate: {error_rate}")
    c.drawString(72, 620, f"CPU Usage: {cpu_usage}")
    c.drawString(72, 600, f"Memory Usage: {mem_usage}")
    c.drawString(72, 580, f"Bid Queue Depth: {queue_depth}")
    c.drawString(72, 560, f"gRPC Error Rate: {grpc_error_rate}")
    c.drawString(72, 540, f"Creative Risk Score: {creative_risk_score}")
    y = 500
    for img in panel_imgs:
        if img:
            img_stream = io.BytesIO(img)
            c.drawImage(img_stream, 72, y, width=400, height=100)
            y -= 120
    c.save()
    print(f"[PDF] Chaos Report saved to {pdf_path}")
    # === NOTIFICATION LOGIC ===
    # Email the PDF report to ops team
    send_pdf_report(
        SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS,
        TO_EMAIL,
        subject="KIKI Chaos Test Audit Report",
        body="See attached PDF for the latest chaos test results.",
        pdf_path=pdf_path
    )
    # Slack notification
    slack_msg = {
        "text": f"KIKI Chaos Test Complete. Blast Radius: {impact_area}, Bids Blocked: {shield_interventions}, Avg Latency: {avg_latency}, Error Rate: {error_rate}. PDF report sent to ops."
    }
    try:
        requests.post(SLACK_WEBHOOK_URL, json=slack_msg, timeout=10)
        print("[Slack] Notification sent.")
    except Exception as e:
        print(f"[Slack] Notification failed: {e}")
    return pdf_path

if __name__ == "__main__":
    generate_chaos_report()
