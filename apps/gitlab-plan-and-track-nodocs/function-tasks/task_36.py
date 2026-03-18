import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    ms = next((m for m in state["milestones"] if m["title"] == "v4.0 Release"), None)
    if not ms:
        return False, "Milestone 'v4.0 Release' not found."

    if ms["state"] != "active":
        return False, f"Expected state 'active', got '{ms['state']}'."

    return True, "Milestone 'v4.0 Release' activated."
