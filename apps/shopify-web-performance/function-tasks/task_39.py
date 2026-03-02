import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    date_grouping = settings.get("dateGrouping")

    if date_grouping != "weekly":
        return False, f"Date grouping is '{date_grouping}', expected 'weekly'."

    return True, "Date grouping is correctly set to 'weekly'."
