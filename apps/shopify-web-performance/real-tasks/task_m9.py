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
        return False, "Could not find theme 'Horizon - Outdoors' in themes list."

    sections_per_page = horizon.get("sectionsPerPage", {})
    home_sections = sections_per_page.get("home")

    if home_sections != 10:
        return False, f"Horizon - Outdoors homepage sections is {home_sections}, expected 10."

    return True, "Horizon - Outdoors homepage sections have been reduced to 10."
