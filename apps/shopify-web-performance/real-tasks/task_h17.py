import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    settings = state.get("settings", {})
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
        sections = prestige.get("sectionsPerPage", {})
        if sections.get("home") != 12:
            errors.append(f"Prestige homepage sections is {sections.get('home')}, expected 12.")

    horizon = next((t for t in themes if t.get("name") == "Horizon - Outdoors"), None)
    if horizon is None:
        errors.append("Could not find theme 'Horizon - Outdoors' in themes list.")
    else:
        if horizon.get("role") != "unpublished":
            errors.append(f"Horizon - Outdoors role is '{horizon.get('role')}', expected 'unpublished'.")

    if settings.get("deviceFilter") != "mobile":
        errors.append(f"Device filter is '{settings.get('deviceFilter')}', expected 'mobile'.")

    if errors:
        return False, " ".join(errors)

    return True, "Prestige published with page transitions off and 12 homepage sections; Horizon unpublished; dashboard on mobile."
