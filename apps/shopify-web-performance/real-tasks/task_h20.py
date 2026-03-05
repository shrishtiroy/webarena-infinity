import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    alerts = settings.get("performanceAlerts", {})
    errors = []

    if alerts.get("alertOnPoor") is not True:
        errors.append(f"alertOnPoor is {alerts.get('alertOnPoor')}, expected True.")
    if alerts.get("alertOnDegradation") is not True:
        errors.append(f"alertOnDegradation is {alerts.get('alertOnDegradation')}, expected True.")
    if alerts.get("emailAlerts") is not True:
        errors.append(f"emailAlerts is {alerts.get('emailAlerts')}, expected True.")
    if alerts.get("lcpThreshold") != 2000:
        errors.append(f"lcpThreshold is {alerts.get('lcpThreshold')}, expected 2000.")
    if alerts.get("inpThreshold") != 150:
        errors.append(f"inpThreshold is {alerts.get('inpThreshold')}, expected 150.")
    if alerts.get("clsThreshold") != 0.05:
        errors.append(f"clsThreshold is {alerts.get('clsThreshold')}, expected 0.05.")
    if alerts.get("degradationPercent") != 10:
        errors.append(f"degradationPercent is {alerts.get('degradationPercent')}, expected 10.")
    if settings.get("reportPercentile") != "p95":
        errors.append(f"reportPercentile is '{settings.get('reportPercentile')}', expected 'p95'.")

    if errors:
        return False, " ".join(errors)

    return True, "Comprehensive performance alerting configured: all alerts enabled, thresholds set, P95 reporting active."
