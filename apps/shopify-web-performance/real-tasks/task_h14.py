import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    errors = []

    horizon = next((t for t in themes if t.get("name") == "Horizon - Outdoors"), None)
    if horizon is None:
        return False, "Could not find theme 'Horizon - Outdoors' in themes list."

    if horizon.get("hasAnimations") is not False:
        errors.append(f"Horizon hasAnimations is {horizon.get('hasAnimations')}, expected False.")

    sections = horizon.get("sectionsPerPage", {})
    expected_sections = {
        "home": 10,
        "product": 6,
        "collection": 4,
        "cart": 2,
        "blog": 3,
    }
    for page_type, expected_val in expected_sections.items():
        actual_val = sections.get(page_type)
        if actual_val != expected_val:
            errors.append(f"Horizon sectionsPerPage.{page_type} is {actual_val}, expected {expected_val}.")

    if errors:
        return False, " ".join(errors)

    return True, "Horizon - Outdoors slimmed down: animations off, all page sections reduced by 2."
