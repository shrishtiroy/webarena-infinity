import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    perf_alerts = settings.get("performanceAlerts", {})
    errors = []

    lcp = perf_alerts.get("lcpThreshold")
    if lcp != 2000:
        errors.append(f"lcpThreshold is {lcp}, expected 2000.")

    inp = perf_alerts.get("inpThreshold")
    if inp != 150:
        errors.append(f"inpThreshold is {inp}, expected 150.")

    cls = perf_alerts.get("clsThreshold")
    if cls != 0.05:
        errors.append(f"clsThreshold is {cls}, expected 0.05.")

    degradation = perf_alerts.get("degradationPercent")
    if degradation != 10:
        errors.append(f"degradationPercent is {degradation}, expected 10.")

    if errors:
        return False, " ".join(errors)

    return True, "All alert thresholds tightened: LCP=2000, INP=150, CLS=0.05, degradationPercent=10."
