import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 119), None)
    if not issue:
        return False, "Issue #119 not found."

    expected = "Fix: Wrap all field values in double quotes before writing to CSV."
    if expected not in (issue.get("description") or ""):
        return False, f"Description does not contain expected fix text."

    return True, "Issue #119 description updated with fix details."
