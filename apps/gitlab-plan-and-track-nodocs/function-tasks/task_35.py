import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    ms = next((m for m in state["milestones"] if m["title"] == "v4.2 Release"), None)
    if not ms:
        return False, "Milestone 'v4.2 Release' not found."

    if ms["state"] != "closed":
        return False, f"Expected state 'closed', got '{ms['state']}'."

    return True, "Milestone 'v4.2 Release' closed."
