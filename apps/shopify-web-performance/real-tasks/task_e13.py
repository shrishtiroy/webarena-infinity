import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    theme = next((t for t in themes if t.get("name") == "Prestige"), None)
    if theme is None:
        return False, "Theme 'Prestige' not found in themes list."

    if theme.get("hasPageTransitions") is not False:
        return False, f"Expected 'Prestige' theme hasPageTransitions to be False, but got '{theme.get('hasPageTransitions')}'."

    return True, "Page transitions have been disabled on the Prestige theme (hasPageTransitions=False)."
