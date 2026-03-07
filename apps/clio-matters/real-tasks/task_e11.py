import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    templates = state.get("matterTemplates", [])
    if not templates:
        return False, "No templates found in state."

    for tmpl in templates:
        name = tmpl.get("name", "")
        if name == "Personal Injury - Auto Accident":
            is_default = tmpl.get("isDefault", False)
            if not is_default:
                return True, "Personal Injury - Auto Accident template is no longer the default."
            else:
                return False, "Personal Injury - Auto Accident template still has isDefault=true."

    return False, "Personal Injury - Auto Accident template not found."
