import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    # Find Department Summary sheet
    sheets = state.get("sheets", [])
    ds = None
    for s in sheets:
        if s.get("name", "").strip() == "Department Summary":
            ds = s
            break
    if ds is None:
        return False, "No sheet named 'Department Summary' found."

    cells = ds.get("cells", {})

    expected = [
        ("Engineering", 8),
        ("Finance", 4),
        ("HR", 3),
        ("Marketing", 5),
        ("Sales", 5),
    ]

    for i, (dept, count) in enumerate(expected):
        row = i + 1
        a_cell = cells.get(f"A{row}", {})
        b_cell = cells.get(f"B{row}", {})

        a_val = str(a_cell.get("value", "")).strip()
        if a_val != dept:
            errors.append(f"A{row} should be '{dept}', got '{a_val}'")

        b_val = b_cell.get("value")
        if b_val != count and str(b_val) != str(count):
            errors.append(f"B{row} should be {count}, got '{b_val}'")

        fmt = a_cell.get("format", {})
        if not fmt.get("bold"):
            errors.append(f"A{row} should be bold")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
