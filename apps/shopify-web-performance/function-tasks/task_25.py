import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    prestige = None
    for theme in themes:
        if theme.get("name") == "Prestige":
            prestige = theme
            break

    if prestige is None:
        return False, "Theme 'Prestige' not found in state."

    sections = prestige.get("sectionsPerPage", {})
    home_val = sections.get("home")
    if home_val != 17:
        return False, f"Prestige sectionsPerPage['home'] is {home_val}, expected 17."

    return True, "Homepage sections for 'Prestige' correctly decreased to 17."
