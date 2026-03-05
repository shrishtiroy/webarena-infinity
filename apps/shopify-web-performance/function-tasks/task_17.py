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

    if horizon.get("hasAnimations") is not False:
        return False, f"Horizon - Outdoors hasAnimations is {horizon.get('hasAnimations')}, expected False."

    return True, "Animations on 'Horizon - Outdoors' are correctly disabled."
