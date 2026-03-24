import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Employees sheet has been renamed to 'Team'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    sheets = state.get("sheets", [])
    for sheet in sheets:
        if sheet.get("name") == "Team":
            return True, "Found a sheet named 'Team'. Rename successful."

    sheet_names = [s.get("name") for s in sheets]
    return False, f"No sheet named 'Team' found. Current sheet names: {sheet_names}"
