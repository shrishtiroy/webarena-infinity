import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    matter = None
    for m in matters:
        if m.get("number") == "00005":
            matter = m
            break

    if matter is None:
        return False, "Could not find matter with number '00005'."

    if matter.get("practiceAreaId") != "pa_6":
        return False, f"Expected matter '00005-Doyle' practiceAreaId to be 'pa_6' (Employment Law), but got '{matter.get('practiceAreaId')}'."

    return True, "Matter '00005-Doyle' practiceAreaId is correctly set to 'pa_6' (Employment Law)."
