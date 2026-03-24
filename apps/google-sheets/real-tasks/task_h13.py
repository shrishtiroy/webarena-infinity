import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    low_stock_sheet = None
    for sheet in sheets:
        if sheet.get("name") == "Low Stock Alert":
            low_stock_sheet = sheet
            break

    if low_stock_sheet is None:
        return False, "Sheet named 'Low Stock Alert' not found."

    cells = low_stock_sheet.get("cells", {})

    expected_headers = {
        "A1": "Product",
        "B1": "Current Stock",
        "C1": "Reorder Level",
    }

    for cell_key, expected_value in expected_headers.items():
        cell = cells.get(cell_key)
        if cell is None:
            errors.append(f"{cell_key} is missing")
            continue

        value = cell.get("value", "")
        if value != expected_value:
            errors.append(f"{cell_key} value is '{value}', expected '{expected_value}'")

        fmt = cell.get("format", {})
        if not fmt.get("bold"):
            errors.append(f"{cell_key} is not bold")

        bg = fmt.get("backgroundColor", "")
        if bg.lower() != "#cfe2f3":
            errors.append(f"{cell_key} backgroundColor is '{bg}', expected '#cfe2f3'")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
