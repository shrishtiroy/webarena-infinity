import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Milestone should not exist
    match = [m for m in state["milestones"] if m["title"] == "Backlog"]
    if match:
        return False, "Milestone 'Backlog' still exists."

    # No issue should reference milestone id 6
    for issue in state["issues"]:
        if issue["milestoneId"] == 6:
            return False, f"Issue #{issue['iid']} still references milestone id 6 (Backlog)."

    return True, "Milestone 'Backlog' deleted and cleared from all issues."
