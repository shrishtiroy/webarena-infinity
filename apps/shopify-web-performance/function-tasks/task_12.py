import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    tags = state.get("tagManagerTags", [])
    target = None
    for tag in tags:
        if tag.get("name") == "Lucky Orange":
            target = tag
            break

    if target is None:
        return False, "Tag 'Lucky Orange' not found in state."

    if target.get("status") != "active":
        return False, f"Tag status is '{target.get('status')}', expected 'active'."

    return True, "Tag 'Lucky Orange' is correctly activated with status='active'."
