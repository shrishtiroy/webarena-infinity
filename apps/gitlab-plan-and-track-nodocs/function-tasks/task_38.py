import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    ms = next((m for m in state["milestones"] if m["title"] == "v4.3 Release"), None)
    if not ms:
        return False, "Milestone 'v4.3 Release' not found."

    if ms["dueDate"] != "2026-07-15":
        return False, f"Expected dueDate '2026-07-15', got '{ms['dueDate']}'."

    return True, "Milestone 'v4.3 Release' due date changed to 2026-07-15."
