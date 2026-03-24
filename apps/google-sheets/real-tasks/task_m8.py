import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Task: Duplicate the Employees sheet and rename the copy to 'Employees Backup'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    sheets = state.get("sheets", [])
    sheet_names = [s.get("name", "") for s in sheets]

    for name in sheet_names:
        if name == "Employees Backup":
            return True, f"Found sheet named 'Employees Backup'. All sheets: {sheet_names}."

    return False, f"No sheet named 'Employees Backup' found. Existing sheets: {sheet_names}."
