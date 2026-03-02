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
        return False, f"emailAlerts is {email_alerts}, expected False."

    return True, "'Email alerts' toggle is correctly disabled."
