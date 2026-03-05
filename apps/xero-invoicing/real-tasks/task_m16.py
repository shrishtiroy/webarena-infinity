import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("brandingThemes", [])
    target = None
    for theme in themes:
        if theme.get("id") == "theme_retail":
            target = theme
            break

    if target is None:
        return False, "Could not find branding theme with id 'theme_retail'."

    name = target.get("name", "")
    if name != "Retail Premium":
        return False, f"Expected theme name 'Retail Premium', but found '{name}'."

    return True, "Branding theme 'theme_retail' renamed to 'Retail Premium'."
