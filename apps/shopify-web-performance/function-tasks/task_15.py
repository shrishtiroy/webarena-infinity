import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    dawn = None
    horizon = None
    for theme in themes:
        if theme.get("name") == "Dawn (backup)":
            dawn = theme
        elif theme.get("name") == "Horizon - Outdoors":
            horizon = theme

    if dawn is None:
        return False, "Theme 'Dawn (backup)' not found in state."

    if horizon is None:
        return False, "Theme 'Horizon - Outdoors' not found in state."

    if dawn.get("role") != "main":
        return False, f"Dawn (backup) role is '{dawn.get('role')}', expected 'main'."

    if dawn.get("status") != "published":
        return False, f"Dawn (backup) status is '{dawn.get('status')}', expected 'published'."

    if horizon.get("role") != "unpublished":
        return False, f"Horizon - Outdoors role is '{horizon.get('role')}', expected 'unpublished'."

    if horizon.get("status") != "unpublished":
        return False, f"Horizon - Outdoors status is '{horizon.get('status')}', expected 'unpublished'."

    selected = state.get("settings", {}).get("selectedThemeId")
    dawn_id = dawn.get("id")
    if selected != dawn_id:
        return False, f"selectedThemeId is '{selected}', expected '{dawn_id}'."

    return True, "Theme 'Dawn (backup)' is correctly published as the main theme."
