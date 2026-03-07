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
        if name == "Flat Fee - Simple Will":
            is_default = tmpl.get("isDefault", False)
            if is_default:
                return True, "Flat Fee - Simple Will template is now the default."
            else:
                return False, "Flat Fee - Simple Will template exists but isDefault is not true."

    return False, "Flat Fee - Simple Will template not found."
