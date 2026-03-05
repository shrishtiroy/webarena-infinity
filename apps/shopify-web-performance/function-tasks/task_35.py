import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    date_range = settings.get("dateRange")

    if date_range != "last_30_days":
        return False, f"Date range is '{date_range}', expected 'last_30_days'."

    return True, "Date range is correctly set to 'last_30_days'."
