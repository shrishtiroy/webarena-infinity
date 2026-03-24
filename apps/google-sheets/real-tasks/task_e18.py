import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that cells A44 through D44 are merged on the Sales sheet."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    sheets = state.get("sheets", [])
    if len(sheets) < 1:
        return False, "No sheets found in application state."

    sales_sheet = sheets[0]
    merged_cells = sales_sheet.get("mergedCells", [])

    if "A44:D44" in merged_cells:
        return True, "Cells A44:D44 are merged on the Sales sheet."

    return False, f"Cells A44:D44 are not in the merged cells list. Current merged cells: {merged_cells}"
