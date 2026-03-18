import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 120), None)
    if not issue:
        return False, "Issue #120 not found."

    milestone = next((m for m in state["milestones"] if m["title"] == "v4.3 Release"), None)
    if not milestone:
        return False, "Milestone 'v4.3 Release' not found."

    if issue["milestoneId"] != milestone["id"]:
        return False, f"Expected milestoneId {milestone['id']}, got {issue['milestoneId']}."

    return True, "Issue #120 milestone set to 'v4.3 Release'."
