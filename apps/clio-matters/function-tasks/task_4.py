import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    deleted_matters = state.get("deletedMatters", [])

    # Check it is NOT in active matters
    for matter in matters:
        desc = matter.get("description", "")
        if "Baker" in desc and "Residential" in desc:
            return False, f"Matter '{desc}' is still in active matters, expected it to be deleted."

    # Check it IS in deletedMatters
    for matter in deleted_matters:
        desc = matter.get("description", "")
        if "Baker" in desc and "Residential" in desc:
            return True, f"Matter '{desc}' was found in deletedMatters as expected."

    return False, "Matter containing 'Baker' and 'Residential' was not found in either matters or deletedMatters."
