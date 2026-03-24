import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    if len(sheets) < 3:
        return False, f"Expected at least 3 sheets, found {len(sheets)}"

    # Expected header columns per sheet
    sheet_headers = {
        "Sales": list("ABCDEFGH"),
        "Employees": list("ABCDEFG"),
        "Inventory": list("ABCDEFGH"),
    }

    for s in sheets[:3]:
        name = s.get("name", "")

        # Check frozen
        if s.get("frozenRows", 0) < 1:
            errors.append(f"'{name}' header row should be frozen")

        # Check header bg
        cols = sheet_headers.get(name)
        if cols is None:
            continue
        cells = s.get("cells", {})
        for col in cols:
            cell = cells.get(f"{col}1", {})
            bg = cell.get("format", {}).get("backgroundColor", "").lower()
            if bg != "#cfe2f3":
                errors.append(f"'{name}'!{col}1 bg should be '#cfe2f3', got '{bg}'")

    # Check named ranges
    named_ranges = state.get("namedRanges", {})
    expected_ranges = {
        "SalesHeaders": "Sales!A1:H1",
        "EmployeeHeaders": "Employees!A1:G1",
        "InventoryHeaders": "Inventory!A1:H1",
    }
    for name, ref in expected_ranges.items():
        actual = named_ranges.get(name)
        if actual is None:
            errors.append(f"Named range '{name}' not found")
        elif actual != ref:
            errors.append(f"'{name}' should be '{ref}', got '{actual}'")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
