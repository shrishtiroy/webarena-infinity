import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    settings = state.get("settings", {})
    alerts = settings.get("performanceAlerts", {})

    if alerts.get("lcpThreshold") != 1500:
        errors.append(f"LCP threshold is {alerts.get('lcpThreshold')}, expected 1500.")
    if alerts.get("inpThreshold") != 100:
        errors.append(f"INP threshold is {alerts.get('inpThreshold')}, expected 100.")
    if alerts.get("clsThreshold") != 0.05:
        errors.append(f"CLS threshold is {alerts.get('clsThreshold')}, expected 0.05.")
    if alerts.get("degradationPercent") != 5:
        errors.append(f"Degradation percent is {alerts.get('degradationPercent')}, expected 5.")
    if settings.get("reportPercentile") != "p95":
        errors.append(f"Report percentile is '{settings.get('reportPercentile')}', expected 'p95'.")

    if errors:
        return False, " ".join(errors)

    return True, "Strict performance monitoring configured: LCP=1500, INP=100, CLS=0.05, degradation=5%, percentile=P95."
