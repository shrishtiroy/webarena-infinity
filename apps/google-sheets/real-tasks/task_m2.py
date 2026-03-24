import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Task: Sort the Inventory sheet by stock level from lowest to highest."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Inventory sheet is at index 2
    sheets = state.get("sheets", [])
    if len(sheets) < 3:
        return False, f"Expected at least 3 sheets, found {len(sheets)}."

    inventory = sheets[2]
    cells = inventory.get("cells", {})

    # Collect D column values from row 2 onwards
    stock_values = []
    row = 2
    while True:
        cell_key = f"D{row}"
        if cell_key not in cells:
            break
        cell = cells[cell_key]
        value = cell.get("value")
        if value is None:
            break
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            break
        stock_values.append(numeric_value)
        row += 1

    if len(stock_values) < 2:
        return False, f"Found only {len(stock_values)} stock values in column D. Expected many more."

    # Check non-decreasing order
    for i in range(len(stock_values) - 1):
        if stock_values[i] > stock_values[i + 1]:
            return False, (
                f"Stock values are not sorted in non-decreasing order. "
                f"Row {i + 2} has {stock_values[i]} but row {i + 3} has {stock_values[i + 1]}."
            )

    return True, f"Inventory sheet is sorted by stock level (lowest to highest). {len(stock_values)} rows verified."
