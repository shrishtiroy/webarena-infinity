import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue_101 = next((i for i in state["issues"] if i["iid"] == 101), None)
    issue_102 = next((i for i in state["issues"] if i["iid"] == 102), None)
    if not issue_101:
        return False, "Issue #101 not found."
    if not issue_102:
        return False, "Issue #102 not found."

    link_101_to_102 = next(
        (r for r in issue_101["relatedIssues"] if r["issueId"] == issue_102["id"]), None
    )
    if link_101_to_102:
        return False, "Issue #101 still has a related issue link to #102."

    link_102_to_101 = next(
        (r for r in issue_102["relatedIssues"] if r["issueId"] == issue_101["id"]), None
    )
    if link_102_to_101:
        return False, "Issue #102 still has a related issue link to #101."

    return True, "Relationship between #101 and #102 removed."
