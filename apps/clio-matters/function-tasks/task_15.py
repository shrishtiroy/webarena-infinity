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

    permissions = matter.get("permissions", {})

    if permissions.get("type") != "specific":
        return False, f"Expected matter '00002-Johnson' permissions.type to be 'specific', but got '{permissions.get('type')}'."

    user_ids = permissions.get("userIds", [])
    if "user_3" not in user_ids:
        return False, f"Expected 'user_3' (Diana Reyes) in matter '00002-Johnson' permissions.userIds, but userIds is {user_ids}."

    return True, "Matter '00002-Johnson' permissions are correctly set to type 'specific' with 'user_3' (Diana Reyes) in userIds."
