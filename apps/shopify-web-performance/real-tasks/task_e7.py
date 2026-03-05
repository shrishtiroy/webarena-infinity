import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    theme = next((t for t in themes if t.get("name") == "Horizon - Outdoors"), None)
    if theme is None:
        return False, "Theme 'Horizon - Outdoors' not found in themes list."

    if theme.get("hasAnimations") is not False:
        return False, f"Expected 'Horizon - Outdoors' theme hasAnimations to be False, but got '{theme.get('hasAnimations')}'."

    return True, "Animations have been disabled on the Horizon - Outdoors theme (hasAnimations=False)."
