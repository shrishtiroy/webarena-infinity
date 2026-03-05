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

    sections = horizon.get("sectionsPerPage", {})
    product_val = sections.get("product")
    if product_val != 7:
        return False, f"Horizon - Outdoors sectionsPerPage['product'] is {product_val}, expected 7."

    return True, "Product sections for 'Horizon - Outdoors' correctly decreased to 7."
