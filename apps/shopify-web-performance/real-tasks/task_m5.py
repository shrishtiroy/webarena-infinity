import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    perf_alerts = settings.get("performanceAlerts", {})
    errors = []

    lcp_threshold = perf_alerts.get("lcpThreshold")
    if lcp_threshold != 2000:
        errors.append(f"LCP alert threshold is {lcp_threshold}, expected 2000.")

    cls_threshold = perf_alerts.get("clsThreshold")
    if cls_threshold != 0.2:
        errors.append(f"CLS alert threshold is {cls_threshold}, expected 0.2.")

    if errors:
        return False, " ".join(errors)

    return True, "LCP alert threshold is set to 2000ms and CLS threshold is set to 0.2."
