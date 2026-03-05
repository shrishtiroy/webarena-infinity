import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    report_percentile = settings.get("reportPercentile")

    if report_percentile != "p90":
        return False, f"Report percentile is '{report_percentile}', expected 'p90'."

    return True, "Report percentile is correctly set to 'p90'."
