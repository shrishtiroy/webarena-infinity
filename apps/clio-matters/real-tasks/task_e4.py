import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    for matter in matters:
        desc = matter.get("description", "") or matter.get("name", "") or ""
        if "Baker" in desc and "Residential" in desc:
            return False, "Baker residential property purchase matter still exists in active matters."

    deleted_matters = state.get("deletedMatters", [])
    for matter in deleted_matters:
        desc = matter.get("description", "") or matter.get("name", "") or ""
        if "Baker" in desc and "Residential" in desc:
            return True, "Baker residential property purchase matter was successfully deleted."

    return False, "Baker residential property purchase matter not found in deletedMatters."
