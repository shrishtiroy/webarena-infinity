import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    tags = state.get("tagManagerTags", [])
    for tag in tags:
        if tag.get("name") == "Snapchat Pixel":
            return False, "Tag 'Snapchat Pixel' still exists in state. It should have been removed."

    return True, "Tag 'Snapchat Pixel' has been successfully removed."
