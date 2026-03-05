import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    horizon = None
    for theme in themes:
        if theme.get("name") == "Horizon - Outdoors":
            horizon = theme
            break

    if horizon is None:
        return False, "Theme 'Horizon - Outdoors' not found in state."

    sections = horizon.get("sectionsPerPage", {})
    home_val = sections.get("home")
    if home_val != 13:
        return False, f"Horizon - Outdoors sectionsPerPage['home'] is {home_val}, expected 13."

    return True, "Homepage sections for 'Horizon - Outdoors' correctly increased to 13."
