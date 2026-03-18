import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Issue #6 blocks both #7 and #8 (the endpoint migration tasks)
    issue = next((i for i in state["issues"] if i["id"] == 6), None)
    if issue is None:
        return False, "Issue #6 not found."

    # Should have documentation label (id 3)
    if 3 not in issue.get("labelIds", []):
        return False, f"Issue #6 does not have the documentation label (id 3). Labels: {issue.get('labelIds')}."

    # Should have 8h (28800s) additional time spent (seed had 12600)
    if issue.get("timeSpent", 0) < 41400:
        return False, f"Issue #6 timeSpent is {issue.get('timeSpent')}, expected at least 41400 (12600 + 28800)."

    return True, "Issue #6 (blocker of both migration tasks) has documentation label and 8h time logged."
