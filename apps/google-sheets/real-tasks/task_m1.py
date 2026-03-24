import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Task: On the Employees sheet, add a formula in cell D27 that totals all salaries."""
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

    if "D27" not in cells:
        return False, "Cell D27 does not exist on the Employees sheet."

    cell = cells["D27"]

    # Check formula contains SUM (case-insensitive)
    formula = cell.get("formula", "")
    if not formula:
        return False, f"Cell D27 has no formula. Value is: {cell.get('value')}"

    if "SUM" not in formula.upper():
        return False, f"Cell D27 formula does not contain SUM. Formula: {formula}"

    # Check formula references D2 through D26
    formula_upper = formula.upper()
    has_d2 = "D2" in formula_upper
    has_d26 = "D26" in formula_upper
    if not (has_d2 and has_d26):
        return False, f"Cell D27 formula does not reference D2 through D26. Formula: {formula}"

    # Check value is a number > 0
    value = cell.get("value")
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return False, f"Cell D27 value is not a number. Value: {value}"

    if numeric_value <= 0:
        return False, f"Cell D27 value should be > 0, got {numeric_value}."

    return True, f"Cell D27 has a SUM formula ({formula}) with value {numeric_value}."
