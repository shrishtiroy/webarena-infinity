import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    perf_alerts = settings.get("performanceAlerts", {})
    cls_threshold = perf_alerts.get("clsThreshold")

    if cls_threshold != 0.25:
        return False, f"clsThreshold is {cls_threshold}, expected 0.25."

    return True, "CLS threshold is correctly set to 0.25."
