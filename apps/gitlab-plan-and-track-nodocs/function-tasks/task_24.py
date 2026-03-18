import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 115), None)
    if not issue:
        return False, "Issue #115 not found."

    # Seed timeSpent is 18000 (5h). After logging 2h30m (9000s), should be 27000.
    expected = 18000 + 9000
    if issue["timeSpent"] != expected:
        return False, f"Expected timeSpent {expected}s (7h30m), got {issue['timeSpent']}."

    return True, "Logged 2h30m on issue #115. Total time spent is now 7h30m."
