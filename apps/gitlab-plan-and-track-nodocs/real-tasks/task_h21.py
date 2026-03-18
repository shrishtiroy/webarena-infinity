import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Issues #7 and #8 should now have priority::high (label 12)
    for issue_id in [7, 8]:
        issue = next((i for i in state["issues"] if i["id"] == issue_id), None)
        if issue is None:
            return False, f"Issue #{issue_id} not found."
        if 12 not in issue.get("labelIds", []):
            return False, f"Issue #{issue_id} does not have priority::high label (id 12). Labels: {issue.get('labelIds')}."

    # Issues #11, #33, #41 (critical priority) should be in Sprint 7 (iteration 7)
    for issue_id in [11, 33, 41]:
        issue = next((i for i in state["issues"] if i["id"] == issue_id), None)
        if issue is None:
            return False, f"Issue #{issue_id} not found."
        if issue.get("iterationId") != 7:
            return False, f"Issue #{issue_id} iterationId is {issue.get('iterationId')}, expected 7 (Sprint 7)."

    return True, "Priority set to high for #7, #8; iteration set to Sprint 7 for #11, #33, #41."
