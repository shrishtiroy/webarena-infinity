import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 101), None)
    if not issue:
        return False, "Issue #101 not found."

    if issue["subscribed"] is not False:
        return False, f"Expected subscribed to be false, got {issue['subscribed']}."

    return True, "Unsubscribed from issue #101."
