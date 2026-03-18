import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 117), None)
    if not issue:
        return False, "Issue #117 not found."

    if issue["weight"] != 7:
        return False, f"Expected weight 7, got {issue['weight']}."

    return True, "Issue #117 weight set to 7."
