import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    perf_alerts = settings.get("performanceAlerts", {})
    degradation_percent = perf_alerts.get("degradationPercent")

    if degradation_percent != 25:
        return False, f"degradationPercent is {degradation_percent}, expected 25."

    return True, "Degradation percentage is correctly set to 25."
