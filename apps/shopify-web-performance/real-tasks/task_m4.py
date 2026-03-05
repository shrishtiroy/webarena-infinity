import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    dawn_backup = None
    horizon = None
    for theme in themes:
        name = theme.get("name", "")
        if name == "Dawn (backup)":
            dawn_backup = theme
        elif name == "Horizon - Outdoors":
            horizon = theme

    if dawn_backup is None:
        return False, "Could not find theme 'Dawn (backup)' in themes list."
    if horizon is None:
        return False, "Could not find theme 'Horizon - Outdoors' in themes list."

    errors = []

    if dawn_backup.get("role") != "main":
        errors.append(f"Dawn (backup) role is '{dawn_backup.get('role')}', expected 'main'.")
    if dawn_backup.get("status") != "published":
        errors.append(f"Dawn (backup) status is '{dawn_backup.get('status')}', expected 'published'.")
    if dawn_backup.get("hasAnimations") is not True:
        errors.append(f"Dawn (backup) hasAnimations is {dawn_backup.get('hasAnimations')}, expected True.")

    if horizon.get("role") != "unpublished":
        errors.append(f"Horizon - Outdoors role is '{horizon.get('role')}', expected 'unpublished'.")

    if errors:
        return False, " ".join(errors)

    return True, "Dawn (backup) is published as main theme with animations enabled, and Horizon - Outdoors is unpublished."
