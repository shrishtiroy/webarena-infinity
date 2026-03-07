import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    matters = state.get("matters", [])

    # Find a NEW matter (not mat_001) for Angela Rodriguez (con_001)
    # with practiceAreaId pa_001, responsibleAttorneyId usr_003, contingency billing at 33.33%
    new_matter = None
    for matter in matters:
        mid = matter.get("id", "")
        client_id = matter.get("clientId", "")
        if client_id == "con_001" and mid != "mat_001":
            new_matter = matter
            break

    if not new_matter:
        return False, "No new matter found for Angela Rodriguez (con_001) besides the existing mat_001."

    errors = []

    # Check practiceAreaId == pa_001
    if new_matter.get("practiceAreaId") != "pa_001":
        errors.append(f"practiceAreaId is '{new_matter.get('practiceAreaId')}', expected 'pa_001' (Personal Injury)")

    # Check responsibleAttorneyId == usr_003
    if new_matter.get("responsibleAttorneyId") != "usr_003":
        errors.append(f"responsibleAttorneyId is '{new_matter.get('responsibleAttorneyId')}', expected 'usr_003' (Maria Garcia)")

    # Check billing preference
    billing = new_matter.get("billingPreference", {})
    if billing.get("billingMethod") != "contingency":
        errors.append(f"billingMethod is '{billing.get('billingMethod')}', expected 'contingency'")
    if billing.get("contingencyRate") != 33.33:
        errors.append(f"contingencyRate is {billing.get('contingencyRate')}, expected 33.33")

    if errors:
        return False, "; ".join(errors)

    return True, "New PI matter created for Angela Rodriguez with Maria Garcia as attorney on contingency at 33.33%."
