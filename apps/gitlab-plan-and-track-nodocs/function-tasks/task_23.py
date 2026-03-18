import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 117), None)
    if not issue:
        return False, "Issue #117 not found."

    expected = 16 * 3600  # 16 hours in seconds
    if issue["timeEstimate"] != expected:
        return False, f"Expected timeEstimate {expected}s (16h), got {issue['timeEstimate']}."

    return True, "Issue #117 time estimate set to 16 hours."
