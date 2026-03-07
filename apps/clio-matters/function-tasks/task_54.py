import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    templates = state.get("matterTemplates", [])
    for tmpl in templates:
        if tmpl.get("name") == "Corporate Transaction - M&A":
            return False, "Template 'Corporate Transaction - M&A' still exists; it should have been deleted."

    return True, "Template 'Corporate Transaction - M&A' has been successfully removed."
