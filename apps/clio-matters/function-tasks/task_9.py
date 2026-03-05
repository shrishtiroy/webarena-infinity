import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    deleted_matters = state.get("deletedMatters", [])

    # Check that the matter exists in active matters
    found_in_active = False
    for m in matters:
        desc = m.get("description", "")
        number = m.get("number", "")
        if "Test Matter" in desc or number == "00099":
            found_in_active = True
            break

    if not found_in_active:
        return False, "Could not find recovered matter with description containing 'Test Matter' or number '00099' in active matters."

    # Check it's no longer in deletedMatters
    still_deleted = False
    for m in deleted_matters:
        desc = m.get("description", "")
        number = m.get("number", "")
        mid = m.get("id", "")
        if "Test Matter" in desc or number == "00099" or mid == "del_matter_2":
            still_deleted = True
            break

    if still_deleted:
        return False, "Matter '00099-TestMatter' was found in active matters but is also still present in deletedMatters."

    return True, "Deleted matter '00099-TestMatter' has been successfully recovered to active matters."
