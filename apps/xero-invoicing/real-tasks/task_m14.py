import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    settings = state.get("invoiceSettings", {})
    due = settings.get("defaultDueDate", {})

    if due.get("type") != "endOfFollowingMonth":
        return False, f"Default due date type is '{due.get('type')}', expected 'endOfFollowingMonth'."

    return True, "Default payment terms set to end of following month."
