import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Task: Use Find and Replace to change all 'Engineering' to 'Product' on the Employees sheet."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Employees sheet is at index 1
    sheets = state.get("sheets", [])
    if len(sheets) < 2:
        return False, f"Expected at least 2 sheets, found {len(sheets)}."

    employees = sheets[1]
    cells = employees.get("cells", {})

    # Check all B column cells
    has_engineering = False
    has_product = False
    engineering_cells = []
    product_cells = []

    for cell_key, cell_data in cells.items():
        if not cell_key.startswith("B"):
            continue
        # Extract row number
        row_str = cell_key[1:]
        try:
            row_num = int(row_str)
        except ValueError:
            continue
        if row_num < 2:
            continue  # Skip header

        value = str(cell_data.get("value", ""))
        if value == "Engineering":
            has_engineering = True
            engineering_cells.append(cell_key)
        if value == "Product":
            has_product = True
            product_cells.append(cell_key)

    if has_engineering:
        return False, f"Found 'Engineering' still present in cells: {engineering_cells}."

    if not has_product:
        return False, "No cell in column B has value 'Product'. The replacement did not occur."

    return True, f"All 'Engineering' values replaced with 'Product'. Product found in: {product_cells}."
