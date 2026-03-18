import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()

    # Label should not exist
    match = [l for l in state["labels"] if l["name"] == "ready-for-dev"]
    if match:
        return False, "Label 'ready-for-dev' still exists."

    # No issue should reference the old label id (9)
    for issue in state["issues"]:
        if 9 in issue.get("labels", []):
            return False, f"Issue #{issue['iid']} still has label id 9 (ready-for-dev)."

    return True, "Label 'ready-for-dev' deleted and removed from all issues."
