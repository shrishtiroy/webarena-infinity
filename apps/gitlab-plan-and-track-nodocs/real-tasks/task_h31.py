import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    epic1 = next((e for e in state["epics"] if e.get("title") == "User Authentication Overhaul"), None)
    if epic1 is None:
        return False, "Epic 'User Authentication Overhaul' not found."

    # Closed children #4, #5 should be removed
    for issue_id in [4, 5]:
        if issue_id in epic1.get("childIssueIds", []):
            return False, f"Closed issue #{issue_id} still in User Authentication Overhaul epic."

    # Notification System Revamp children #63, #64, #65 should be added
    for issue_id in [63, 64, 65]:
        if issue_id not in epic1.get("childIssueIds", []):
            return False, f"Issue #{issue_id} not in User Authentication Overhaul epic childIssueIds."

    return True, "Closed children removed and Notification System Revamp children added to User Authentication Overhaul."
