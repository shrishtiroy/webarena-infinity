import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])

    # Find Foster matter
    foster = None
    for matter in matters:
        desc = matter.get("description", "") or ""
        mid = matter.get("id", "")
        if ("Foster" in desc and "Evanston" in desc) or mid == "mat_002":
            foster = matter
            break

    if not foster:
        return False, "Could not find the Foster v. City of Evanston matter in state."

    damages = foster.get("damages", [])
    if len(damages) != 0:
        return False, f"Foster case still has {len(damages)} damage(s); expected 0 (all deleted)."

    return True, "All damages deleted from the Foster slip-and-fall case."
