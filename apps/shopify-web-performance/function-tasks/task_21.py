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

    if prestige.get("hasPageTransitions") is not False:
        return False, f"Prestige hasPageTransitions is {prestige.get('hasPageTransitions')}, expected False."

    return True, "Page transitions on 'Prestige' are correctly disabled."
