import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    epic = next((e for e in state["epics"] if e.get("title") == "Compliance Audit"), None)
    if epic is None:
        return False, "Epic 'Compliance Audit' not found."

    if not epic.get("confidential"):
        return False, f"Epic 'Compliance Audit' is not confidential."

    if 5 not in epic.get("labels", []):
        return False, f"Label 'security' (id 5) not in epic labels: {epic.get('labels')}."

    if 11 not in epic.get("labels", []):
        return False, f"Label 'priority::critical' (id 11) not in epic labels: {epic.get('labels')}."

    # v3.0 security issues: #46, #57, #58, #59
    expected_children = [46, 57, 58, 59]
    for issue_id in expected_children:
        if issue_id not in epic.get("childIssueIds", []):
            return False, f"Issue #{issue_id} not in epic childIssueIds: {epic.get('childIssueIds')}."

    # Each child should have priority::critical (11)
    for issue_id in expected_children:
        issue = next((i for i in state["issues"] if i["id"] == issue_id), None)
        if issue is None:
            return False, f"Issue #{issue_id} not found."
        if 11 not in issue.get("labelIds", []):
            return False, f"Issue #{issue_id} does not have priority::critical (id 11). Labels: {issue.get('labelIds')}."

    return True, "Confidential epic 'Compliance Audit' created with security+critical labels, children #46-#59 with critical priority."
