import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # #23 "Keyboard navigation..." should have weight 13
    issue23 = next((i for i in state["issues"] if i["id"] == 23), None)
    if issue23 is None:
        return False, "Issue #23 not found."
    if issue23.get("weight") != 13:
        return False, f"Issue #23 weight is {issue23.get('weight')}, expected 13."

    # #23 should block #96 "Add keyboard shortcuts..."
    if not any(r.get("issueId") == 96 and r.get("type") == "blocks" for r in issue23.get("relatedIssues", [])):
        return False, f"Issue #23 does not have a 'blocks' relationship with #96. Related: {issue23.get('relatedIssues')}."

    issue96 = next((i for i in state["issues"] if i["id"] == 96), None)
    if issue96 is None:
        return False, "Issue #96 not found."
    if not any(r.get("issueId") == 23 and r.get("type") == "is_blocked_by" for r in issue96.get("relatedIssues", [])):
        return False, f"Issue #96 does not have an 'is_blocked_by' relationship with #23. Related: {issue96.get('relatedIssues')}."

    return True, "Issue #23 weight set to 13 and blocks relationship added to #96."
