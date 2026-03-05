import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    errors = []

    device_filter = settings.get("deviceFilter")
    if device_filter != "mobile":
        errors.append(f"Device filter is '{device_filter}', expected 'mobile'.")

    date_range = settings.get("dateRange")
    if date_range != "today":
        errors.append(f"Date range is '{date_range}', expected 'today'.")

    if errors:
        return False, " ".join(errors)

    return True, "Device view is set to mobile and date range is set to today."
