import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    hotjar_app = next((a for a in apps if "Hotjar" in a.get("name", "")), None)
    if hotjar_app is not None:
        return False, f"Hotjar app still exists in apps list: '{hotjar_app.get('name')}'."

    return True, "Hotjar Heatmaps & Recordings app has been uninstalled (no longer in apps list)."
