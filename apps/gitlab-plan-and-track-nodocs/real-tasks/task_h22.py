import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Jun Nakamura (id 4) has the highest total weight — should be assigned to #60, #61, #62
    for issue_id in [60, 61, 62]:
        issue = next((i for i in state["issues"] if i["id"] == issue_id), None)
        if issue is None:
            return False, f"Issue #{issue_id} not found."
        if 4 not in issue.get("assigneeIds", []):
            return False, f"Jun Nakamura (id 4) not in assigneeIds for issue #{issue_id}: {issue.get('assigneeIds')}."

    return True, "Jun Nakamura assigned to all unassigned Search Infrastructure Upgrade children (#60, #61, #62)."
