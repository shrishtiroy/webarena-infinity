import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    notif = next(
        (n for n in state["notificationFeed"]
         if "Marcus Johnson assigned you to issue #105" in n.get("message", "")),
        None,
    )
    if not notif:
        return False, "Notification about 'Marcus Johnson assigned you to issue #105' not found."

    if notif["read"] is not True:
        return False, f"Expected notification to be read, got read={notif['read']}."

    return True, "Notification marked as read."
