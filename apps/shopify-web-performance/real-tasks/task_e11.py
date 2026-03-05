import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    device_filter = settings.get("deviceFilter")
    if device_filter != "mobile":
        return False, f"Expected settings.deviceFilter to be 'mobile', but got '{device_filter}'."

    return True, "Performance data has been filtered to mobile devices only (deviceFilter=mobile)."
