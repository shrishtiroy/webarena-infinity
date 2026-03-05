import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    branding_themes = state.get("brandingThemes", [])
    for theme in branding_themes:
        if theme.get("name") == "Simple Clean":
            return False, "Branding theme 'Simple Clean' still exists."

    return True, "Branding theme 'Simple Clean' has been successfully removed."
