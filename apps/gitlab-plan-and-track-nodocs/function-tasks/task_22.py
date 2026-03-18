import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 116), None)
    if not issue:
        return False, "Issue #116 not found."

    if issue["weight"] != 4:
        return False, f"Expected weight 4, got {issue['weight']}."

    return True, "Issue #116 weight set to 4 via /weight quick action."
