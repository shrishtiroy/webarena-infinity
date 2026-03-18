import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue_115 = next((i for i in state["issues"] if i["iid"] == 115), None)
    issue_121 = next((i for i in state["issues"] if i["iid"] == 121), None)
    if not issue_115:
        return False, "Issue #115 not found."
    if not issue_121:
        return False, "Issue #121 not found."

    # Check issue #115 has a 'blocks' link to #121
    link = next((r for r in issue_115["relatedIssues"] if r["issueId"] == issue_121["id"]), None)
    if not link:
        return False, "Issue #115 does not have a related issue link to #121."
    if link["linkType"] != "blocks":
        return False, f"Expected linkType 'blocks', got '{link['linkType']}'."

    # Check reverse: #121 has 'is_blocked_by' link to #115
    reverse = next((r for r in issue_121["relatedIssues"] if r["issueId"] == issue_115["id"]), None)
    if not reverse:
        return False, "Issue #121 does not have a reverse related issue link to #115."
    if reverse["linkType"] != "is_blocked_by":
        return False, f"Expected reverse linkType 'is_blocked_by', got '{reverse['linkType']}'."

    return True, "Issue #121 added as blocking issue on #115."
