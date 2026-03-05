import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matter = None
    for m in matters:
        if m.get("number") == "00002":
            matter = m
            break

    if matter is None:
        return False, "Could not find matter with number '00002'."

    if matter.get("status") != "closed":
        return False, f"Expected matter '00002-Johnson' status to be 'closed', but got '{matter.get('status')}'."

    if not matter.get("closedDate"):
        return False, "Matter '00002-Johnson' status is 'closed' but closedDate is null or missing."

    return True, "Matter '00002-Johnson' is correctly closed with a closedDate set."
