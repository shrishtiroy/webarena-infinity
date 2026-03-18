import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    val = state.get("notificationSettings", {}).get("email", {}).get("newComment")
    if val is not False:
        return False, f"Expected email.newComment to be false, got {val}."

    return True, "Email notification for new comments disabled."
