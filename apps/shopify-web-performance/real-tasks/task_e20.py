import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    show_annotations = settings.get("showAnnotations")
    if show_annotations is not False:
        return False, f"Expected settings.showAnnotations to be False, but got '{show_annotations}'."

    return True, "Event annotations on performance charts have been hidden (showAnnotations=False)."
