import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue_117 = next((i for i in state["issues"] if i["iid"] == 117), None)
    issue_115 = next((i for i in state["issues"] if i["iid"] == 115), None)
    if not issue_117:
        return False, "Issue #117 not found."
    if not issue_115:
        return False, "Issue #115 not found."

    link = next((r for r in issue_117["relatedIssues"] if r["issueId"] == issue_115["id"]), None)
    if not link:
        return False, "Issue #117 does not have a related issue link to #115."
    if link["linkType"] != "relates_to":
        return False, f"Expected linkType 'relates_to', got '{link['linkType']}'."

    reverse = next((r for r in issue_115["relatedIssues"] if r["issueId"] == issue_117["id"]), None)
    if not reverse:
        return False, "Issue #115 does not have a reverse related issue link to #117."

    return True, "Issues #117 and #115 linked as 'relates to'."
