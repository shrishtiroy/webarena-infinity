import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    date_range = settings.get("dateRange")
    if date_range != "last_30_days":
        return False, f"Expected settings.dateRange to be 'last_30_days', but got '{date_range}'."

    return True, "Dashboard date range has been changed to last 30 days (dateRange=last_30_days)."
