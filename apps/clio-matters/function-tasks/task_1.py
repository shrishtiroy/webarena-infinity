import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matter = None
    for m in matters:
        if m.get("number") == "00001" or "Patterson" in m.get("displayNumber", ""):
            matter = m
            break

    if matter is None:
        return False, "Could not find matter '00001-Patterson'."

    if matter.get("status") != "pending":
        return False, f"Expected matter '00001-Patterson' status to be 'pending', but got '{matter.get('status')}'."

    return True, "Matter '00001-Patterson' status is correctly set to 'pending'."
