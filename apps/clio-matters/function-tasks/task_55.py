import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matching = [m for m in matters if m.get("number") == "00001"]
    if not matching:
        return False, "Matter with number '00001' not found."

    matter = matching[0]
    staff_id = matter.get("responsibleStaffId")
    if staff_id != "user_9":
        return False, f"Expected matter '00001' responsibleStaffId 'user_9' (Angela Martinez), got '{staff_id}'."

    return True, "Matter '00001-Patterson' responsibleStaffId is correctly set to 'user_9' (Angela Martinez)."
