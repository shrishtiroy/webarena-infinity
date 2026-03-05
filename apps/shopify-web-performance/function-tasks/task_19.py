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

    if prestige.get("hasAnimations") is not False:
        return False, f"Prestige hasAnimations is {prestige.get('hasAnimations')}, expected False."

    return True, "Animations on 'Prestige' are correctly disabled."
