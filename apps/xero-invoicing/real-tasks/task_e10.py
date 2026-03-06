import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    prof = next((t for t in state["brandingThemes"] if t["id"] == "theme_professional"), None)
    if not prof:
        return False, "Professional Services theme not found."

    if not prof["isDefault"]:
        return False, "Professional Services theme is not set as default."

    others = [t for t in state["brandingThemes"] if t["id"] != "theme_professional" and t["isDefault"]]
    if others:
        return False, f"Other theme(s) are also marked as default: {[t['name'] for t in others]}"

    return True, "Professional Services is the default branding theme."
