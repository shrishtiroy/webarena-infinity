import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    match = [i for i in state["issues"] if i["title"] == "Implement dark mode toggle"]
    if not match:
        return False, "Issue 'Implement dark mode toggle' not found."

    issue = match[0]
    if issue["state"] != "opened":
        return False, f"Expected state 'opened', got '{issue['state']}'."

    return True, "Issue 'Implement dark mode toggle' created successfully."
