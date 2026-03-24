import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the Sales sheet by name
    sales_sheet = None
    for sheet in state["sheets"]:
        if sheet["name"] == "Sales":
            sales_sheet = sheet
            break

    if sales_sheet is None:
        return False, "No sheet named 'Sales' found."

    frozen_rows = sales_sheet.get("frozenRows", 0)
    if frozen_rows == 1:
        return True, "Top row is frozen on the Sales sheet (frozenRows == 1)."
    return False, f"Expected frozenRows to be 1 on Sales sheet, but found {frozen_rows}."
