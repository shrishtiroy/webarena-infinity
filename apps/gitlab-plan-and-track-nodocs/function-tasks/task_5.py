import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 111), None)
    if not issue:
        return False, "Issue #111 not found."

    if issue["state"] != "opened":
        return False, f"Expected state 'opened', got '{issue['state']}'."
    if issue["closedAt"] is not None:
        return False, f"Expected closedAt to be null, got '{issue['closedAt']}'."

    return True, "Issue #111 reopened successfully."
