import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    perf_alerts = settings.get("performanceAlerts", {})
    inp_threshold = perf_alerts.get("inpThreshold")

    if inp_threshold != 300:
        return False, f"inpThreshold is {inp_threshold}, expected 300."

    return True, "INP threshold is correctly set to 300."
