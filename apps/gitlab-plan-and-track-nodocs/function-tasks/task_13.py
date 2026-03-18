import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    issue = next((i for i in state["issues"] if i["iid"] == 120), None)
    if not issue:
        return False, "Issue #120 not found."

    epic = next((e for e in state["epics"] if e["title"] == "Accessibility Compliance (WCAG 2.1 AA)"), None)
    if not epic:
        return False, "Epic 'Accessibility Compliance (WCAG 2.1 AA)' not found."

    if issue["epicId"] != epic["id"]:
        return False, f"Expected epicId {epic['id']}, got {issue['epicId']}."

    return True, "Issue #120 epic set to 'Accessibility Compliance (WCAG 2.1 AA)'."
