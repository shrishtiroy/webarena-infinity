import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    errors = []

    report_percentile = settings.get("reportPercentile")
    if report_percentile != "p90":
        errors.append(f"Report percentile is '{report_percentile}', expected 'p90'.")

    date_grouping = settings.get("dateGrouping")
    if date_grouping != "weekly":
        errors.append(f"Date grouping is '{date_grouping}', expected 'weekly'.")

    if errors:
        return False, " ".join(errors)

    return True, "Report percentile is set to P90 and date grouping is set to weekly."
