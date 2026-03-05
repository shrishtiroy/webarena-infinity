import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])

    # Look for a matter whose description contains both 'Patterson v. Metro Transit Authority' and '(Copy)'
    duplicate = None
    for m in matters:
        desc = m.get("description", "")
        if "Patterson v. Metro Transit Authority" in desc and "(Copy)" in desc:
            duplicate = m
            break

    if duplicate is None:
        return False, "Could not find a duplicate of matter_1. Expected a matter with description containing 'Patterson v. Metro Transit Authority' and '(Copy)'."

    errors = []

    if duplicate.get("clientId") != "contact_1":
        errors.append(f"Expected duplicate matter clientId to be 'contact_1', but got '{duplicate.get('clientId')}'.")

    if duplicate.get("practiceAreaId") != "pa_1":
        errors.append(f"Expected duplicate matter practiceAreaId to be 'pa_1', but got '{duplicate.get('practiceAreaId')}'.")

    if errors:
        return False, "Duplicate matter found but has issues: " + " ".join(errors)

    return True, "A duplicate of matter_1 (Patterson v. Metro Transit Authority) exists with correct clientId and practiceAreaId."
