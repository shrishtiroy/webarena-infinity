import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    perf_alerts = settings.get("performanceAlerts", {})
    lcp_threshold = perf_alerts.get("lcpThreshold")

    if lcp_threshold != 3000:
        return False, f"lcpThreshold is {lcp_threshold}, expected 3000."

    return True, "LCP threshold is correctly set to 3000."
