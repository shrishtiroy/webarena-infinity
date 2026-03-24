import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Employees sheet is at index 1
    sheets = state.get("sheets", [])
    emp_sheet = None
    for s in sheets:
        if s.get("name", "").lower() in ("employees", "team directory"):
            emp_sheet = s
            break
    if emp_sheet is None and len(sheets) > 1:
        emp_sheet = sheets[1]
    if emp_sheet is None:
        return False, "Employees sheet not found."

    cells = emp_sheet.get("cells", {})

    # Check all A2:A26 are bold
    for row in range(2, 27):
        cell_key = f"A{row}"
        cell = cells.get(cell_key, {})
        fmt = cell.get("format", {})
        if not fmt.get("bold"):
            errors.append(f"{cell_key} should be bold")

    # Check all B2:B26 are italic
    for row in range(2, 27):
        cell_key = f"B{row}"
        cell = cells.get(cell_key, {})
        fmt = cell.get("format", {})
        if not fmt.get("italic"):
            errors.append(f"{cell_key} should be italic")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
