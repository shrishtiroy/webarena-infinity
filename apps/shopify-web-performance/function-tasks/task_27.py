import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    themes = state.get("themes", [])

    dawn = None
    for theme in themes:
        if theme.get("name") == "Dawn (backup)":
            dawn = theme
            break

    if dawn is None:
        return False, "Theme 'Dawn (backup)' not found in state."

    sections = dawn.get("sectionsPerPage", {})
    collection_val = sections.get("collection")
    if collection_val != 4:
        return False, f"Dawn (backup) sectionsPerPage['collection'] is {collection_val}, expected 4."

    return True, "Collection sections for 'Dawn (backup)' correctly decreased to 4."
