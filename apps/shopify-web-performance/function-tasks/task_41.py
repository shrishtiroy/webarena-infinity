import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    show_annotations = settings.get("showAnnotations")

    if show_annotations is not False:
        return False, f"showAnnotations is {show_annotations}, expected False."

    return True, "Show event annotations is correctly disabled (False)."
