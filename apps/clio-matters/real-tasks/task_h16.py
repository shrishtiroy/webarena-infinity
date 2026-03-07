import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    templates = state.get("matterTemplates", [])

    errors = []

    # Check that no template named "Criminal Defense - Misdemeanor" exists
    for tmpl in templates:
        if tmpl.get("name") == "Criminal Defense - Misdemeanor":
            errors.append("Template 'Criminal Defense - Misdemeanor' still exists; should have been renamed")
            break

    # Check that "Criminal Defense - General" exists with correct properties
    target = None
    for tmpl in templates:
        if tmpl.get("name") == "Criminal Defense - General":
            target = tmpl
            break

    if not target:
        errors.append("No template named 'Criminal Defense - General' found")
    else:
        if target.get("responsibleAttorneyId") != "usr_006":
            errors.append(f"Template responsibleAttorneyId is '{target.get('responsibleAttorneyId')}', expected 'usr_006' (Michael Osei)")
        if target.get("responsibleStaffId") != "usr_009":
            errors.append(f"Template responsibleStaffId is '{target.get('responsibleStaffId')}', expected 'usr_009' (Lisa Patel)")

    if errors:
        return False, "; ".join(errors)

    return True, "Criminal Defense template renamed to 'General', attorney set to Michael Osei, staff set to Lisa Patel."
