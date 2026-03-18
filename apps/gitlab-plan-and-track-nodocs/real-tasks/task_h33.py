import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Issues co-assigned to Jun (4) and Emily (8): #15, #23, #30
    for issue_id in [15, 23, 30]:
        issue = next((i for i in state["issues"] if i["id"] == issue_id), None)
        if issue is None:
            return False, f"Issue #{issue_id} not found."
        if issue.get("weight") != 13:
            return False, f"Issue #{issue_id} weight is {issue.get('weight')}, expected 13."
        if 11 not in issue.get("labelIds", []):
            return False, f"Issue #{issue_id} does not have priority::critical label (id 11). Labels: {issue.get('labelIds')}."

    return True, "Issues #15, #23, #30 (co-assigned to Jun and Emily) set to weight 13 and priority::critical."
