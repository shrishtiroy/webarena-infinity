import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    dawn = None
    for theme in themes:
        if theme.get("name") == "Dawn (backup)":
            dawn = theme
            break

    if dawn is None:
        return False, "Theme 'Dawn (backup)' not found in state."

    if dawn.get("hasAnimations") is not True:
        return False, f"Dawn (backup) hasAnimations is {dawn.get('hasAnimations')}, expected True."

    return True, "Animations on 'Dawn (backup)' are correctly enabled."
