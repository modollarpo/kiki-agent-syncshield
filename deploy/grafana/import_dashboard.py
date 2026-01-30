import requests
import os

def import_grafana_dashboard(grafana_url, api_key, dashboard_json_path):
    with open(dashboard_json_path, 'r') as f:
        dashboard_json = f.read()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    url = f"{grafana_url}/api/dashboards/import"
    resp = requests.post(url, headers=headers, data=dashboard_json)
    resp.raise_for_status()
    print(f"[Grafana] Dashboard imported: {resp.json().get('slug')}")

if __name__ == "__main__":
    GRAFANA_URL = os.environ.get("GRAFANA_URL", "http://localhost:3000")
    GRAFANA_API_KEY = os.environ.get("GRAFANA_API_KEY", "YOUR_GRAFANA_API_KEY")
    DASHBOARD_JSON_PATH = os.environ.get("DASHBOARD_JSON_PATH", "kiki_chaos_dashboard.json")
    import_grafana_dashboard(GRAFANA_URL, GRAFANA_API_KEY, DASHBOARD_JSON_PATH)
