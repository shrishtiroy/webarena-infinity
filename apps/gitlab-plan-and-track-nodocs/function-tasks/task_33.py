import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    match = [m for m in state["milestones"] if m["title"] == "v4.4 Release"]
    if not match:
        return False, "Milestone 'v4.4 Release' not found."

    ms = match[0]
    if ms["description"] != "Q3 improvements and stability fixes":
        return False, f"Expected description 'Q3 improvements and stability fixes', got '{ms['description']}'."
    if ms["startDate"] != "2026-07-01":
        return False, f"Expected startDate '2026-07-01', got '{ms['startDate']}'."
    if ms["dueDate"] != "2026-09-30":
        return False, f"Expected dueDate '2026-09-30', got '{ms['dueDate']}'."
    if ms["state"] != "active":
        return False, f"Expected state 'active', got '{ms['state']}'."

    return True, "Milestone 'v4.4 Release' created with correct details."
