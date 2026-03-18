import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # v2.0 open issues with weight=8 and exactly 1 assignee: #3, #7, #11, #22, #33, #49, #55, #113
    expected = [3, 7, 11, 22, 33, 49, 55, 113]
    for issue_id in expected:
        issue = next((i for i in state["issues"] if i["id"] == issue_id), None)
        if issue is None:
            return False, f"Issue #{issue_id} not found."
        if issue.get("weight") != 13:
            return False, f"Issue #{issue_id} weight is {issue.get('weight')}, expected 13."

    return True, "Weight set to 13 for all v2.0 single-assignee weight-8 issues (#3, #7, #11, #22, #33, #49, #55, #113)."
