import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the first two columns are frozen on the Employees sheet."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    sheets = state.get("sheets", [])
    if len(sheets) < 2:
        return False, "Expected at least 2 sheets but found fewer."

    employees_sheet = sheets[1]
    frozen_cols = employees_sheet.get("frozenCols", 0)

    if frozen_cols == 2:
        return True, "The Employees sheet has 2 frozen columns."

    return False, f"The Employees sheet does not have 2 frozen columns. frozenCols = {frozen_cols}"
