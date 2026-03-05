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
        return False, "Could not find theme 'Prestige' in themes list."

    errors = []

    if prestige.get("hasAnimations") is not False:
        errors.append(f"Prestige hasAnimations is {prestige.get('hasAnimations')}, expected False.")
    if prestige.get("hasPageTransitions") is not False:
        errors.append(f"Prestige hasPageTransitions is {prestige.get('hasPageTransitions')}, expected False.")

    if errors:
        return False, " ".join(errors)

    return True, "Both animations and page transitions are turned off on the Prestige theme."
