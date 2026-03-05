import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    notifications = state.get("notificationSettings", {})
    budget_threshold = notifications.get("budget_threshold")
    if budget_threshold is not False:
        return False, f"Expected notificationSettings budget_threshold to be False, got '{budget_threshold}'."

    return True, "Notification setting budget_threshold is correctly set to False."
