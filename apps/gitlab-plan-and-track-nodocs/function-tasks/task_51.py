import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    for notif in state.get("notificationFeed", []):
        if notif["read"] is not True:
            return False, f"Notification id {notif['id']} is still unread."

    return True, "All notifications marked as read."
