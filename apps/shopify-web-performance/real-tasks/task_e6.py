import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    dawn_backup = next((t for t in themes if t.get("name") == "Dawn (backup)"), None)
    if dawn_backup is None:
        return False, "Theme 'Dawn (backup)' not found in themes list."

    if dawn_backup.get("role") != "main":
        return False, f"Expected 'Dawn (backup)' theme role to be 'main', but got '{dawn_backup.get('role')}'."

    if dawn_backup.get("status") != "published":
        return False, f"Expected 'Dawn (backup)' theme status to be 'published', but got '{dawn_backup.get('status')}'."

    horizon = next((t for t in themes if t.get("name") == "Horizon - Outdoors"), None)
    if horizon is None:
        return False, "Theme 'Horizon - Outdoors' not found in themes list."

    if horizon.get("role") != "unpublished":
        return False, f"Expected 'Horizon - Outdoors' theme role to be 'unpublished', but got '{horizon.get('role')}'."

    return True, "Live theme switched to Dawn (backup) (role=main, status=published) and Horizon - Outdoors is now unpublished."
