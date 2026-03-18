import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # #12 should block #60
    issue12 = next((i for i in state["issues"] if i["id"] == 12), None)
    if issue12 is None:
        return False, "Issue #12 not found."
    if not any(r.get("issueId") == 60 and r.get("type") == "blocks" for r in issue12.get("relatedIssues", [])):
        return False, f"Issue #12 does not have a 'blocks' relationship with #60. Related: {issue12.get('relatedIssues')}."

    issue60 = next((i for i in state["issues"] if i["id"] == 60), None)
    if issue60 is None:
        return False, "Issue #60 not found."
    if not any(r.get("issueId") == 12 and r.get("type") == "is_blocked_by" for r in issue60.get("relatedIssues", [])):
        return False, f"Issue #60 does not have an 'is_blocked_by' relationship with #12. Related: {issue60.get('relatedIssues')}."

    # Both should have priority::high (12)
    if 12 not in issue12.get("labelIds", []):
        return False, f"Issue #12 does not have priority::high (id 12). Labels: {issue12.get('labelIds')}."
    if 12 not in issue60.get("labelIds", []):
        return False, f"Issue #60 does not have priority::high (id 12). Labels: {issue60.get('labelIds')}."

    return True, "Blocks relationship from #12 to #60 added, both have priority::high."
