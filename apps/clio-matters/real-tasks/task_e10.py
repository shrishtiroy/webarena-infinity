import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    templates = state.get("matterTemplates", [])

    for tmpl in templates:
        name = tmpl.get("name", "")
        if name == "Corporate Transaction - M&A":
            return False, "Corporate Transaction - M&A template still exists."

    return True, "Corporate Transaction - M&A template has been deleted."
