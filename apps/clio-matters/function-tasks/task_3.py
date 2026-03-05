import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matter = None
    for m in matters:
        if m.get("number") == "00003":
            matter = m
            break

    if matter is None:
        return False, "Could not find matter with number '00003'."

    if matter.get("status") != "open":
        return False, f"Expected matter '00003-Russo' status to be 'open' (reopened), but got '{matter.get('status')}'."

    return True, "Matter '00003-Russo' has been successfully reopened with status 'open'."
