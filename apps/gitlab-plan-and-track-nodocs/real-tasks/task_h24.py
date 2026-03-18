import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    moved_issues = [15, 16, 17, 51]

    # Check issues removed from Mobile Responsive (epic 4)
    epic4 = next((e for e in state["epics"] if e.get("title") == "Mobile Responsive Redesign"), None)
    if epic4 is None:
        return False, "Epic 'Mobile Responsive Redesign' not found."
    for issue_id in moved_issues:
        if issue_id in epic4.get("childIssueIds", []):
            return False, f"Issue #{issue_id} still in Mobile Responsive Redesign epic."

    # Check issues added to Accessibility Compliance (epic 6)
    epic6 = next((e for e in state["epics"] if "Accessibility Compliance" in e.get("title", "")), None)
    if epic6 is None:
        return False, "Epic 'Accessibility Compliance' not found."
    for issue_id in moved_issues:
        if issue_id not in epic6.get("childIssueIds", []):
            return False, f"Issue #{issue_id} not in Accessibility Compliance epic childIssueIds."

    # Check priority set to high (label 12) on each
    priority_labels = {11, 12, 13, 14}
    for issue_id in moved_issues:
        issue = next((i for i in state["issues"] if i["id"] == issue_id), None)
        if issue is None:
            return False, f"Issue #{issue_id} not found."
        if 12 not in issue.get("labelIds", []):
            return False, f"Issue #{issue_id} does not have priority::high (id 12). Labels: {issue.get('labelIds')}."

    return True, "Issues #15, #16, #17, #51 moved from Mobile Responsive to Accessibility Compliance with priority::high."
