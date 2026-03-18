import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 117), None)
    if not issue:
        return False, "Issue #117 not found."

    lisa = next((u for u in state["users"] if u["name"] == "Lisa Wang"), None)
    if not lisa:
        return False, "User 'Lisa Wang' not found."

    if lisa["id"] not in issue["assignees"]:
        return False, f"Lisa Wang (id {lisa['id']}) not in assignees: {issue['assignees']}."

    return True, "Lisa Wang assigned to issue #117 via quick action."
