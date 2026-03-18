import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    match = [m for m in state["milestones"] if m["title"] == "v4.1 Patch"]
    if match:
        return False, "Milestone 'v4.1 Patch' still exists."

    # Verify no issues still reference this milestone
    for issue in state["issues"]:
        if issue["milestoneId"] == 2:
            return False, f"Issue #{issue['iid']} still references deleted milestone id 2."

    return True, "Milestone 'v4.1 Patch' deleted and cleared from issues."
