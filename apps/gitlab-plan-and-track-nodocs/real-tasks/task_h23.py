import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Issues #7, #8, #10, #47 (breaking-change in v2.0) should be closed
    for issue_id in [7, 8, 10, 47]:
        issue = next((i for i in state["issues"] if i["id"] == issue_id), None)
        if issue is None:
            return False, f"Issue #{issue_id} not found."
        if issue["status"] != "closed":
            return False, f"Issue #{issue_id} status is '{issue['status']}', expected 'closed'."

    return True, "All open breaking-change issues in v2.0 (#7, #8, #10, #47) are closed."
