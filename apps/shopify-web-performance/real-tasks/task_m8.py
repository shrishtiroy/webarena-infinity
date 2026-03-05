import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    perf_alerts = settings.get("performanceAlerts", {})
    errors = []

    if perf_alerts.get("alertOnPoor") is not False:
        errors.append(f"alertOnPoor is {perf_alerts.get('alertOnPoor')}, expected False.")
    if perf_alerts.get("alertOnDegradation") is not False:
        errors.append(f"alertOnDegradation is {perf_alerts.get('alertOnDegradation')}, expected False.")
    if perf_alerts.get("emailAlerts") is not False:
        errors.append(f"emailAlerts is {perf_alerts.get('emailAlerts')}, expected False.")

    if errors:
        return False, " ".join(errors)

    return True, "All performance alert notifications are turned off (alertOnPoor, alertOnDegradation, emailAlerts all False)."
