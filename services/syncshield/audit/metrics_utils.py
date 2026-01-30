import requests

def get_prometheus_metric(prom_url, query):
    resp = requests.get(f"{prom_url}/api/v1/query", params={"query": query})
    resp.raise_for_status()
    data = resp.json()
    if data['status'] == 'success' and data['data']['result']:
        return data['data']['result'][0]['value'][1]
    return None

def get_grafana_panel_image(grafana_url, api_key, panel_id, dashboard_uid, from_ts, to_ts, width=1000, height=500):
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "panelId": panel_id,
        "dashboardUid": dashboard_uid,
        "from": from_ts,
        "to": to_ts,
        "width": width,
        "height": height,
        "tz": "UTC"
    }
    url = f"{grafana_url}/render/d-solo/{dashboard_uid}/_?panelId={panel_id}"
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.content
