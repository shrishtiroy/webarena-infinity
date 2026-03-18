import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 123), None)
    if not issue:
        return False, "Issue #123 not found."

    if issue["dueDate"] != "2026-04-10":
        return False, f"Expected dueDate '2026-04-10', got '{issue['dueDate']}'."

    return True, "Issue #123 due date set to 2026-04-10."
