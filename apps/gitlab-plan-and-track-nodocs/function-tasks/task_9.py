import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 107), None)
    if not issue:
        return False, "Issue #107 not found."

    david = next((u for u in state["users"] if u["name"] == "David Thompson"), None)
    if not david:
        return False, "User 'David Thompson' not found."

    if david["id"] not in issue["assignees"]:
        return False, f"David Thompson (id {david['id']}) not in assignees: {issue['assignees']}."

    return True, "David Thompson assigned to issue #107."
