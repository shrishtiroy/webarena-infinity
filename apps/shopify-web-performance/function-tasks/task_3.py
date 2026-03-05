import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    apps = state.get("apps", [])
    for app in apps:
        if app.get("name") == "Hotjar Heatmaps & Recordings":
            return False, "App 'Hotjar Heatmaps & Recordings' still exists in state. It should have been removed."

    return True, "App 'Hotjar Heatmaps & Recordings' has been successfully removed."
