import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    templates = state.get("matterTemplates", [])
    flat_fee_template = None
    pi_template = None

    for tmpl in templates:
        if tmpl.get("name") == "Flat Fee - Simple Will":
            flat_fee_template = tmpl
        if tmpl.get("name") == "Personal Injury - Auto Accident":
            pi_template = tmpl

    if flat_fee_template is None:
        return False, "Template 'Flat Fee - Simple Will' not found."
    if not flat_fee_template.get("isDefault"):
        return False, "Template 'Flat Fee - Simple Will' is not set as default."

    if pi_template is None:
        return False, "Template 'Personal Injury - Auto Accident' not found."
    if pi_template.get("isDefault"):
        return False, "Template 'Personal Injury - Auto Accident' is still set as default; only one default is allowed."

    return True, "'Flat Fee - Simple Will' is default and 'Personal Injury - Auto Accident' is no longer default."
