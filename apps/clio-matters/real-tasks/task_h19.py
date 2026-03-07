import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])
    deleted_matters = state.get("deletedMatters", [])

    errors = []

    # Check 1: Nguyen matter has status == "Closed"
    nguyen = None
    for matter in matters:
        desc = matter.get("description", "") or ""
        mid = matter.get("id", "")
        if "Nguyen" in desc or mid == "mat_005":
            nguyen = matter
            break

    if not nguyen:
        errors.append("Nguyen matter not found in matters list")
    elif nguyen.get("status") != "Closed":
        errors.append(f"Nguyen status is '{nguyen.get('status')}', expected 'Closed'")

    # Check 2: Midwest Manufacturing has status == "Open"
    midwest = None
    for matter in matters:
        desc = matter.get("description", "") or ""
        mid = matter.get("id", "")
        if "Midwest" in desc or mid == "mat_006":
            midwest = matter
            break

    if not midwest:
        errors.append("Midwest Manufacturing matter not found in matters list")
    elif midwest.get("status") != "Open":
        errors.append(f"Midwest Manufacturing status is '{midwest.get('status')}', expected 'Open'")

    # Check 3: Baker - Residential Property is NOT in matters, and IS in deletedMatters
    baker_in_matters = False
    for matter in matters:
        desc = matter.get("description", "") or ""
        mid = matter.get("id", "")
        if ("Baker" in desc and "Residential" in desc) or mid == "mat_010":
            baker_in_matters = True
            break

    if baker_in_matters:
        errors.append("Baker - Residential Property matter still exists in active matters; should have been deleted")

    baker_in_deleted = False
    for dm in deleted_matters:
        desc = dm.get("description", "") or ""
        mid = dm.get("id", "")
        if ("Baker" in desc) or mid == "mat_010":
            baker_in_deleted = True
            break

    if not baker_in_deleted:
        errors.append("Baker matter not found in deletedMatters")

    if errors:
        return False, "; ".join(errors)

    return True, "Nguyen closed, Midwest Manufacturing reopened, Baker deleted."
