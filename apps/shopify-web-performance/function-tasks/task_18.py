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

    if horizon.get("hasPageTransitions") is not True:
        return False, f"Horizon - Outdoors hasPageTransitions is {horizon.get('hasPageTransitions')}, expected True."

    return True, "Page transitions on 'Horizon - Outdoors' are correctly enabled."
