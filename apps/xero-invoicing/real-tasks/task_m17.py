import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("brandingThemes", [])
    target = None
    for theme in themes:
        if theme.get("id") == "theme_professional":
            target = theme
            break

    if target is None:
        return False, "Could not find branding theme with id 'theme_professional'."

    expected = "All work is subject to our Master Services Agreement. Payment terms are strictly net 30 days."
    actual = target.get("termsAndConditions", "")
    if actual != expected:
        return False, f"Expected termsAndConditions to be '{expected}', but found '{actual}'."

    return True, "Professional Services template terms and conditions updated correctly."
