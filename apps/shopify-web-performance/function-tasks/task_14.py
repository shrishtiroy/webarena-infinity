import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    tags = state.get("tagManagerTags", [])
    for tag in tags:
        if tag.get("name") == "Affirm Messaging":
            return False, "Tag 'Affirm Messaging' still exists in state. It should have been removed."

    return True, "Tag 'Affirm Messaging' has been successfully removed."
