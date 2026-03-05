import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    tags = state.get("tagManagerTags", [])
    tag = next((t for t in tags if t.get("name") == "Pinterest Tag"), None)
    if tag is None:
        return False, "Tag 'Pinterest Tag' not found in tagManagerTags list."

    if tag.get("status") != "active":
        return False, f"Expected Pinterest Tag status to be 'active', but got '{tag.get('status')}'."

    return True, "Pinterest Tag has been activated (status=active)."
