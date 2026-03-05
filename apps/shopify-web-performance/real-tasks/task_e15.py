import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    settings = state.get("settings", {})
    comparison_enabled = settings.get("comparisonEnabled")
    if comparison_enabled is not False:
        return False, f"Expected settings.comparisonEnabled to be False, but got '{comparison_enabled}'."

    return True, "Similar stores comparison has been turned off (comparisonEnabled=False)."
