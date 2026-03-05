import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    tags = state.get("tagManagerTags", [])
    target = None
    for tag in tags:
        if tag.get("name") == "Google Analytics 4":
            target = tag
            break

    if target is None:
        return False, "Tag 'Google Analytics 4' not found in state."

    if target.get("status") != "inactive":
        return False, f"Tag status is '{target.get('status')}', expected 'inactive'."

    return True, "Tag 'Google Analytics 4' is correctly deactivated with status='inactive'."
