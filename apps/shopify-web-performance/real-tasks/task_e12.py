import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    perf_alerts = settings.get("performanceAlerts", {})
    email_alerts = perf_alerts.get("emailAlerts")
    if email_alerts is not False:
        return False, f"Expected settings.performanceAlerts.emailAlerts to be False, but got '{email_alerts}'."

    return True, "Email performance alerts have been turned off (emailAlerts=False)."
