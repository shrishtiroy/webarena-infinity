import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    templates = state.get("matterTemplates", [])
    for tmpl in templates:
        if tmpl.get("name") == "Personal Injury - Auto Accident":
            if tmpl.get("isDefault"):
                return False, "Template 'Personal Injury - Auto Accident' is still set as default."
            return True, "Template 'Personal Injury - Auto Accident' has isDefault set to False."

    return False, "Template 'Personal Injury - Auto Accident' not found in matterTemplates."
