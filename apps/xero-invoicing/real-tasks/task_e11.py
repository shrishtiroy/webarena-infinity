import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    simple = next((t for t in state["brandingThemes"] if t["id"] == "theme_simple"), None)
    if simple is not None:
        return False, "Simple Clean theme still exists."

    return True, "Simple Clean branding theme removed successfully."
