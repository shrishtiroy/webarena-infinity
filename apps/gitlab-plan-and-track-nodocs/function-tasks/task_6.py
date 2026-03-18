import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 105), None)
    if not issue:
        return False, "Issue #105 not found."

    if issue["title"] != "Add mobile-first responsive navigation":
        return False, f"Expected title 'Add mobile-first responsive navigation', got '{issue['title']}'."

    return True, "Issue #105 title updated successfully."
