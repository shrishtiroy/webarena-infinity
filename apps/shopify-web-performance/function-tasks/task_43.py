import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    perf_alerts = settings.get("performanceAlerts", {})
    alert_on_poor = perf_alerts.get("alertOnPoor")

    if alert_on_poor is not False:
        return False, f"alertOnPoor is {alert_on_poor}, expected False."

    return True, "'Alert on poor ranking' toggle is correctly disabled."
