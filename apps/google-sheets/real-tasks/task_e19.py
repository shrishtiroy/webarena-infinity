import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Sales sheet has been duplicated (a sheet named 'Sales (Copy)' exists)."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    sheets = state.get("sheets", [])
    for sheet in sheets:
        if sheet.get("name") == "Sales (Copy)":
            return True, "Found a sheet named 'Sales (Copy)'. Duplication successful."

    sheet_names = [s.get("name") for s in sheets]
    return False, f"No sheet named 'Sales (Copy)' found. Current sheet names: {sheet_names}"
