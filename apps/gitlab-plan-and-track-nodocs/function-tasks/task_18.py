import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 101), None)
    if not issue:
        return False, "Issue #101 not found."

    marcus = next((u for u in state["users"] if u["name"] == "Marcus Johnson"), None)
    if not marcus:
        return False, "User 'Marcus Johnson' not found."

    if marcus["id"] in issue["assignees"]:
        return False, f"Marcus Johnson (id {marcus['id']}) is still in assignees: {issue['assignees']}."

    return True, "Marcus Johnson removed from issue #101 assignees."
