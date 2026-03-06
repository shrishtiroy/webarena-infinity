import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    theme = next((t for t in state["brandingThemes"] if t["name"] == "Corporate"), None)
    if not theme:
        return False, "Branding theme 'Corporate' not found."

    return True, "Branding theme 'Corporate' created successfully."
