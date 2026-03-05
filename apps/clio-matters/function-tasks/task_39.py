import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    templates = state.get("matterTemplates", [])
    matching = [t for t in templates if t.get("name") == "Estate Planning - Comprehensive"]
    if matching:
        return False, "Template 'Estate Planning - Comprehensive' still exists in matterTemplates but should have been deleted."

    return True, "Template 'Estate Planning - Comprehensive' has been successfully deleted."
