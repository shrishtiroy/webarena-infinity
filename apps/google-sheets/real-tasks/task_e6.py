import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    active_sheet = state.get("activeSheet")
    if active_sheet == 1:
        return True, "Active sheet is the Employees sheet (index 1)."
    return False, f"Expected activeSheet to be 1 (Employees), but found {active_sheet}."
