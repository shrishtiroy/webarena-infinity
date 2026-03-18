import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    match = [i for i in state["issues"] if i["title"] == "Update CI pipeline configuration"]
    if not match:
        return False, "Issue 'Update CI pipeline configuration' not found."

    issue = match[0]
    if issue["type"] != "task":
        return False, f"Expected type 'task', got '{issue['type']}'."
    if issue["weight"] != 3:
        return False, f"Expected weight 3, got {issue['weight']}."

    return True, "Task 'Update CI pipeline configuration' created with weight 3."
