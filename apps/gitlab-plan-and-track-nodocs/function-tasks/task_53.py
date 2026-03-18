import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    val = state.get("notificationSettings", {}).get("email", {}).get("closedIssue")
    if val is not True:
        return False, f"Expected email.closedIssue to be true, got {val}."

    return True, "Email notification for closed issues enabled."
