import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    device_filter = settings.get("deviceFilter")

    if device_filter != "desktop":
        return False, f"Device filter is '{device_filter}', expected 'desktop'."

    return True, "Device filter is correctly set to 'desktop'."
