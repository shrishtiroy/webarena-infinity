import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    deleted_matters = state.get("deletedMatters", [])

    # Check matter with number '00008' is NOT in active matters
    in_active = False
    for m in matters:
        if m.get("number") == "00008":
            in_active = True
            break

    # Check if it exists in deletedMatters
    in_deleted = False
    for m in deleted_matters:
        if m.get("number") == "00008" or m.get("id") == "matter_8":
            in_deleted = True
            break

    if in_active:
        return False, "Matter '00008-Mills' is still in the active matters array. It should have been deleted."

    if not in_active and not in_deleted:
        # It's gone from both — could be permanently deleted, which still counts
        return True, "Matter '00008-Mills' has been deleted (not found in active matters)."

    if in_deleted:
        return True, "Matter '00008-Mills' has been successfully moved to deletedMatters."

    return False, "Unexpected state for matter '00008-Mills'."
