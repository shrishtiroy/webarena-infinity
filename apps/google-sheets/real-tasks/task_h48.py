import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    idx_sheet = None
    for s in sheets:
        if s.get("name", "").strip() == "Workbook Index":
            idx_sheet = s
            break
    if idx_sheet is None:
        return False, f"No sheet named 'Workbook Index' found. Sheets: {[s['name'] for s in sheets]}"

    cells = idx_sheet.get("cells", {})

    # Check headers
    for col, header in [("A", "Sheet"), ("B", "Rows"), ("C", "Columns")]:
        cell = cells.get(f"{col}1", {})
        if str(cell.get("value", "")).strip() != header:
            errors.append(f"{col}1 should be '{header}', got '{cell.get('value', '')}'")
        fmt = cell.get("format", {})
        if not fmt.get("bold"):
            errors.append(f"{col}1 should be bold")
        if str(fmt.get("backgroundColor", "")).lower() != "#e0e0e0":
            errors.append(f"{col}1 bg should be '#e0e0e0'")

    # Check data rows
    expected = [
        ("Sales", 40, 8),
        ("Employees", 25, 7),
        ("Inventory", 30, 8),
    ]
    for i, (name, rows, cols) in enumerate(expected):
        row = i + 2
        a_val = str(cells.get(f"A{row}", {}).get("value", "")).strip()
        if a_val != name:
            errors.append(f"A{row} should be '{name}', got '{a_val}'")
        b_val = cells.get(f"B{row}", {}).get("value")
        if b_val != rows and str(b_val) != str(rows):
            errors.append(f"B{row} should be {rows}, got '{b_val}'")
        c_val = cells.get(f"C{row}", {}).get("value")
        if c_val != cols and str(c_val) != str(cols):
            errors.append(f"C{row} should be {cols}, got '{c_val}'")

    # Check named ranges
    named = state.get("namedRanges", {})
    expected_ranges = {
        "SalesData": "Sales!A2:H41",
        "EmployeeData": "Employees!A2:G26",
        "InventoryData": "Inventory!A2:H31",
    }
    for name, expected_val in expected_ranges.items():
        if name not in named:
            errors.append(f"Named range '{name}' not found")
        elif named[name] != expected_val:
            errors.append(f"'{name}' should be '{expected_val}', got '{named[name]}'")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "Workbook Index sheet and named ranges created correctly."
