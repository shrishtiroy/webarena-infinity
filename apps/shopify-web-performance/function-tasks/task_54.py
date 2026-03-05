import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    errors = []

    date_grouping = settings.get("dateGrouping")
    if date_grouping != "monthly":
        errors.append(f"dateGrouping is '{date_grouping}', expected 'monthly'.")

    report_percentile = settings.get("reportPercentile")
    if report_percentile != "p95":
        errors.append(f"reportPercentile is '{report_percentile}', expected 'p95'.")

    if errors:
        return False, " ".join(errors)

    return True, "Date grouping is correctly set to 'monthly' and report percentile is correctly set to 'p95'."
