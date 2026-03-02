import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    perf_alerts = settings.get("performanceAlerts", {})
    alert_on_degradation = perf_alerts.get("alertOnDegradation")

    if alert_on_degradation is not False:
        return False, f"alertOnDegradation is {alert_on_degradation}, expected False."

    return True, "'Alert on degradation' toggle is correctly disabled."
