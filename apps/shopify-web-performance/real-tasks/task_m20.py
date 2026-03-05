import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    errors = []

    device_filter = settings.get("deviceFilter")
    if device_filter != "desktop":
        errors.append(f"Device filter is '{device_filter}', expected 'desktop'.")

    report_percentile = settings.get("reportPercentile")
    if report_percentile != "p50":
        errors.append(f"Report percentile is '{report_percentile}', expected 'p50'.")

    if errors:
        return False, " ".join(errors)

    return True, "Device view is set to desktop and report percentile is set to P50."
