import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 106), None)
    if not issue:
        return False, "Issue #106 not found."

    expected = "This needs to be prioritized for the next sprint"
    comments = [a for a in issue.get("activities", []) if a["type"] == "comment"]
    match = [c for c in comments if expected in c["content"]]
    if not match:
        return False, "Comment not found on issue #106."

    return True, "Comment added to issue #106."
