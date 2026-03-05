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

    blocked_users = matter.get("blockedUsers", [])
    if "user_5" not in blocked_users:
        return False, f"Expected 'user_5' (Priya Sharma) in matter '00001-Patterson' blockedUsers, but blockedUsers is {blocked_users}."

    return True, "Matter '00001-Patterson' blockedUsers correctly contains 'user_5' (Priya Sharma)."
