import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])
    errors = []

    dawn = next((t for t in themes if t.get("name") == "Dawn (backup)"), None)
    if dawn is None:
        errors.append("Could not find theme 'Dawn (backup)' in themes list.")
    else:
        if dawn.get("role") != "main":
            errors.append(f"Dawn (backup) role is '{dawn.get('role')}', expected 'main'.")
        if dawn.get("status") != "published":
            errors.append(f"Dawn (backup) status is '{dawn.get('status')}', expected 'published'.")
        sections = dawn.get("sectionsPerPage", {})
        if sections.get("home") != 6:
            errors.append(f"Dawn (backup) homepage sections is {sections.get('home')}, expected 6.")
        if dawn.get("hasAnimations") is not True:
            errors.append(f"Dawn (backup) hasAnimations is {dawn.get('hasAnimations')}, expected True.")

    horizon = next((t for t in themes if t.get("name") == "Horizon - Outdoors"), None)
    if horizon is None:
        errors.append("Could not find theme 'Horizon - Outdoors' in themes list.")
    else:
        if horizon.get("role") != "unpublished":
            errors.append(f"Horizon - Outdoors role is '{horizon.get('role')}', expected 'unpublished'.")

    if errors:
        return False, " ".join(errors)

    return True, "Dawn (backup) is published with 6 homepage sections and animations enabled; Horizon - Outdoors is unpublished."
