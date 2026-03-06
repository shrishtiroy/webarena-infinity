import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    theme = next((t for t in state["brandingThemes"] if t["id"] == "theme_standard"), None)
    if not theme:
        return False, "Standard theme not found."

    if theme.get("showTaxNumber") is not False:
        return False, f"Standard theme showTaxNumber is {theme.get('showTaxNumber')}, expected False."

    return True, "ABN hidden on Standard template."
