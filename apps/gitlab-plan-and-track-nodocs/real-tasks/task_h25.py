import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Tom Ramirez (6), v2.1 (ms 4), devops (label 9): #19, #20, #21, #42, #50, #53
    for issue_id in [19, 20, 21, 42, 50, 53]:
        issue = next((i for i in state["issues"] if i["id"] == issue_id), None)
        if issue is None:
            return False, f"Issue #{issue_id} not found."
        if issue["status"] != "closed":
            return False, f"Issue #{issue_id} status is '{issue['status']}', expected 'closed'."

    return True, "All Tom Ramirez's devops issues in v2.1 (#19, #20, #21, #42, #50, #53) are closed."
