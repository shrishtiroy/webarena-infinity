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

    sections_per_page = prestige.get("sectionsPerPage", {})
    product_sections = sections_per_page.get("product")

    if product_sections != 14:
        return False, f"Prestige product page sections is {product_sections}, expected 14."

    return True, "Prestige theme product page sections have been increased to 14."
