import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Unassigned backend issues in v2.1: #60, #61, #63, #64, #80, #111
    target_issues = [60, 61, 63, 64, 80, 111]

    for issue_id in target_issues:
        issue = next((i for i in state["issues"] if i["id"] == issue_id), None)
        if issue is None:
            return False, f"Issue #{issue_id} not found."
        if 3 not in issue.get("assigneeIds", []):
            return False, f"Ana Garcia (id 3) not in assigneeIds for issue #{issue_id}: {issue.get('assigneeIds')}."
        if issue.get("iterationId") != 8:
            return False, f"Issue #{issue_id} iterationId is {issue.get('iterationId')}, expected 8 (Sprint 8)."

    return True, "Ana Garcia assigned and Sprint 8 set for all unassigned backend issues in v2.1."
