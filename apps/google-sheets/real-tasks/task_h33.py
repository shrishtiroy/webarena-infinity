import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])

    # Check first sheet is "Team"
    if not sheets or sheets[0].get("name", "") != "Team":
        actual = sheets[0].get("name", "") if sheets else "none"
        errors.append(f"First sheet should be 'Team', got '{actual}'")

    # Find Archive sheet
    archive = None
    for s in sheets:
        if s.get("name", "").strip() == "Archive":
            archive = s
            break
    if archive is None:
        return False, "No sheet named 'Archive' found."

    cells = archive.get("cells", {})

    # Check headers
    headers = [("A1", "Sheet Name"), ("B1", "Row Count"), ("C1", "Status")]
    for addr, expected in headers:
        cell = cells.get(addr, {})
        if str(cell.get("value", "")).strip() != expected:
            errors.append(f"{addr} should be '{expected}', got '{cell.get('value', '')}'")
        fmt = cell.get("format", {})
        if not fmt.get("bold"):
            errors.append(f"{addr} should be bold")
        bg = fmt.get("backgroundColor", "").lower()
        if bg != "#e0e0e0":
            errors.append(f"{addr} bg should be '#e0e0e0', got '{bg}'")

    # Check data rows
    data_rows = [
        (2, "Team", 25, "Active"),
        (3, "Sales", 40, "Active"),
        (4, "Inventory", 30, "Active"),
    ]
    for row, name, count, status in data_rows:
        a = cells.get(f"A{row}", {})
        b = cells.get(f"B{row}", {})
        c = cells.get(f"C{row}", {})

        if str(a.get("value", "")).strip() != name:
            errors.append(f"A{row} should be '{name}', got '{a.get('value', '')}'")
        b_val = b.get("value")
        if b_val != count and str(b_val) != str(count):
            errors.append(f"B{row} should be {count}, got '{b_val}'")
        if str(c.get("value", "")).strip() != status:
            errors.append(f"C{row} should be '{status}', got '{c.get('value', '')}'")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
