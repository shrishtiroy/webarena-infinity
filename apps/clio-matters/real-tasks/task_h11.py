import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    templates = state.get("matterTemplates", [])

    errors = []

    # Check that no template named "Flat Fee - Simple Will" exists
    for tmpl in templates:
        if tmpl.get("name") == "Flat Fee - Simple Will":
            errors.append("Template 'Flat Fee - Simple Will' still exists; should have been renamed")
            break

    # Check that "Estate Planning - Comprehensive" exists with correct properties
    target = None
    for tmpl in templates:
        if tmpl.get("name") == "Estate Planning - Comprehensive":
            target = tmpl
            break

    if not target:
        errors.append("No template named 'Estate Planning - Comprehensive' found")
    else:
        if target.get("billingMethod") != "hourly":
            errors.append(f"Template billingMethod is '{target.get('billingMethod')}', expected 'hourly'")
        if target.get("responsibleStaffId") != "usr_009":
            errors.append(f"Template responsibleStaffId is '{target.get('responsibleStaffId')}', expected 'usr_009' (Lisa Patel)")

    if errors:
        return False, "; ".join(errors)

    return True, "Flat Fee template renamed to 'Estate Planning - Comprehensive', billing set to hourly, staff set to Lisa Patel."
