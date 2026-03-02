import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."

    state = resp.json()
    themes = state.get("brandingThemes", [])
    if not themes:
        return False, "No branding themes found in state."

    target = next((t for t in themes if t["id"] == "theme_professional"), None)
    if not target:
        return False, "Branding theme 'theme_professional' not found."

    if target["isDefault"] is not True:
        return False, f"Theme 'Professional Services' isDefault is {target['isDefault']}, expected True."

    others_with_default = [t for t in themes if t["id"] != "theme_professional" and t.get("isDefault") is True]
    if others_with_default:
        names = ", ".join(t["name"] for t in others_with_default)
        return False, f"Other themes still have isDefault=True: {names}."

    return True, "Professional Services is now the default branding theme, and all other themes have isDefault=False."
