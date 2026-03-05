import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    errors = []

    prestige = next((t for t in themes if t.get("name") == "Prestige"), None)
    if prestige is None:
        errors.append("Could not find theme 'Prestige' in themes list.")
    else:
        if prestige.get("role") != "main":
            errors.append(f"Prestige role is '{prestige.get('role')}', expected 'main'.")
        if prestige.get("status") != "published":
            errors.append(f"Prestige status is '{prestige.get('status')}', expected 'published'.")
        if prestige.get("hasPageTransitions") is not False:
            errors.append(f"Prestige hasPageTransitions is {prestige.get('hasPageTransitions')}, expected False.")
        if prestige.get("hasAnimations") is not False:
            errors.append(f"Prestige hasAnimations is {prestige.get('hasAnimations')}, expected False.")
        sections = prestige.get("sectionsPerPage", {})
        if sections.get("home") != 15:
            errors.append(f"Prestige homepage sections is {sections.get('home')}, expected 15.")

    horizon = next((t for t in themes if t.get("name") == "Horizon - Outdoors"), None)
    if horizon is None:
        errors.append("Could not find theme 'Horizon - Outdoors' in themes list.")
    else:
        if horizon.get("role") != "unpublished":
            errors.append(f"Horizon - Outdoors role is '{horizon.get('role')}', expected 'unpublished'.")

    if errors:
        return False, " ".join(errors)

    return True, "Prestige is published with page transitions and animations disabled, homepage sections at 15; Horizon is unpublished."
