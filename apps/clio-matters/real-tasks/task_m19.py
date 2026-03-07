import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find Personal Injury practice area id
    practice_areas = state.get("practiceAreas", [])
    pi_id = None
    for pa in practice_areas:
        if pa.get("name") == "Personal Injury":
            pi_id = pa.get("id", "")
            break
    if not pi_id:
        pi_id = "pa_001"

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or ""
        matter_id = matter.get("id", "")
        if "Kowalski" in desc or matter_id == "mat_014":
            pa = matter.get("practiceAreaId", "")
            if pa == pi_id:
                return True, "Kowalski workers comp matter practice area changed to Personal Injury."
            else:
                return False, f"Kowalski matter practiceAreaId is '{pa}', expected '{pi_id}' (Personal Injury)."

    return False, "Could not find the Kowalski matter in state."
