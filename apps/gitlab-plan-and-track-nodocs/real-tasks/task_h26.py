import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # #2 (SAML in Auth epic) should block #57 (SAML in SSO epic)
    issue2 = next((i for i in state["issues"] if i["id"] == 2), None)
    if issue2 is None:
        return False, "Issue #2 not found."
    if not any(r.get("issueId") == 57 and r.get("type") == "blocks" for r in issue2.get("relatedIssues", [])):
        return False, f"Issue #2 does not have a 'blocks' relationship with issue #57. Related: {issue2.get('relatedIssues')}."

    issue57 = next((i for i in state["issues"] if i["id"] == 57), None)
    if issue57 is None:
        return False, "Issue #57 not found."
    if not any(r.get("issueId") == 2 and r.get("type") == "is_blocked_by" for r in issue57.get("relatedIssues", [])):
        return False, f"Issue #57 does not have an 'is_blocked_by' relationship with issue #2. Related: {issue57.get('relatedIssues')}."

    return True, "Blocks relationship added from #2 (Auth SAML) to #57 (SSO SAML)."
