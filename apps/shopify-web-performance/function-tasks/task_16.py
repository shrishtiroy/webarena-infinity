import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    prestige = None
    horizon = None
    for theme in themes:
        if theme.get("name") == "Prestige":
            prestige = theme
        elif theme.get("name") == "Horizon - Outdoors":
            horizon = theme

    if prestige is None:
        return False, "Theme 'Prestige' not found in state."

    if horizon is None:
        return False, "Theme 'Horizon - Outdoors' not found in state."

    if prestige.get("role") != "main":
        return False, f"Prestige role is '{prestige.get('role')}', expected 'main'."

    if prestige.get("status") != "published":
        return False, f"Prestige status is '{prestige.get('status')}', expected 'published'."

    if horizon.get("role") != "unpublished":
        return False, f"Horizon - Outdoors role is '{horizon.get('role')}', expected 'unpublished'."

    if horizon.get("status") != "unpublished":
        return False, f"Horizon - Outdoors status is '{horizon.get('status')}', expected 'unpublished'."

    selected = state.get("settings", {}).get("selectedThemeId")
    prestige_id = prestige.get("id")
    if selected != prestige_id:
        return False, f"selectedThemeId is '{selected}', expected '{prestige_id}'."

    return True, "Theme 'Prestige' is correctly published as the main theme."
