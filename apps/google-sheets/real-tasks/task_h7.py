import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Inventory sheet (originally index 2)
    sheets = state.get("sheets", [])
    inv_sheet = None
    for s in sheets:
        if s.get("name", "").lower() in ("inventory", "stock management"):
            inv_sheet = s
            break
    if inv_sheet is None and len(sheets) > 2:
        inv_sheet = sheets[2]
    if inv_sheet is None:
        return False, "Inventory sheet not found."

    cells = inv_sheet.get("cells", {})

    # Collect category values from column C, rows 2-31
    category_values = []
    has_accessories = False
    has_peripherals = False
    has_addons = False
    has_hardware = False

    for row in range(2, 32):
        cell_key = f"C{row}"
        cell = cells.get(cell_key, {})
        val = str(cell.get("value", "")).strip()
        if val:
            category_values.append(val)
            if val.lower() == "accessories":
                has_accessories = True
            if val.lower() == "peripherals":
                has_peripherals = True
            if val.lower() == "add-ons":
                has_addons = True
            if val.lower() == "hardware":
                has_hardware = True

    # Check 1: No "Accessories" or "Peripherals" remain
    if has_accessories:
        errors.append("Column C still contains 'Accessories' -- should have been replaced with 'Add-ons'")
    if has_peripherals:
        errors.append("Column C still contains 'Peripherals' -- should have been replaced with 'Hardware'")

    # Check 2: At least one "Add-ons" and one "Hardware"
    if not has_addons:
        errors.append("No cell in column C has value 'Add-ons'")
    if not has_hardware:
        errors.append("No cell in column C has value 'Hardware'")

    # Check 3: Category values in ascending alphabetical order
    if len(category_values) >= 2:
        sorted_values = sorted(category_values, key=lambda x: x.lower())
        if category_values != sorted_values:
            errors.append("Category column (C) is not sorted in ascending alphabetical order")
    else:
        errors.append(f"Expected category values in C2:C31, found only {len(category_values)}")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
