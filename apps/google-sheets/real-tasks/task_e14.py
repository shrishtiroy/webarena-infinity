import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that cell I1 on the Sales sheet contains the value 'Notes'."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    sheets = state.get("sheets", [])
    if len(sheets) < 1:
        return False, "No sheets found in application state."

    sales_sheet = sheets[0]
    cells = sales_sheet.get("cells", {})

    cell_i1 = cells.get("I1", {})
    value = cell_i1.get("value")

    if value == "Notes":
        return True, "Cell I1 on the Sales sheet contains 'Notes'."

    return False, f"Cell I1 on the Sales sheet does not contain 'Notes'. Found value: {repr(value)}"
