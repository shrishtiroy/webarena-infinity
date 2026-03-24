import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that Oliver Grant's salary has been changed to 200000 on the Employees sheet."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    sheets = state.get("sheets", [])
    if len(sheets) < 2:
        return False, "Expected at least 2 sheets but found fewer."

    employees_sheet = sheets[1]
    cells = employees_sheet.get("cells", {})

    target_row = None
    for addr, cell in cells.items():
        if addr.startswith("A") and cell.get("value") == "Oliver Grant":
            target_row = addr[1:]
            break

    if target_row is None:
        return False, "Could not find 'Oliver Grant' in column A of the Employees sheet."

    salary_addr = f"D{target_row}"
    salary_cell = cells.get(salary_addr, {})
    salary_value = salary_cell.get("value")

    # Handle both numeric and string representations
    try:
        salary_numeric = float(salary_value)
    except (TypeError, ValueError):
        return False, f"Cell {salary_addr} does not contain a numeric value. Found: {repr(salary_value)}"

    if salary_numeric == 200000:
        return True, f"Oliver Grant's salary in cell {salary_addr} is correctly set to 200000."

    return False, f"Oliver Grant's salary in cell {salary_addr} is {salary_value}, expected 200000."
