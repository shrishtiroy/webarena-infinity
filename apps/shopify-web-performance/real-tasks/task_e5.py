import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    tags = state.get("tagManagerTags", [])
    tag = next((t for t in tags if t.get("name") == "Snapchat Pixel"), None)
    if tag is not None:
        return False, "Snapchat Pixel tag still exists in tagManagerTags list."

    return True, "Snapchat Pixel tag has been removed (no longer in tagManagerTags list)."
