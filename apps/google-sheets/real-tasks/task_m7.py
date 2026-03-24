import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Task: Add data validation to Priya Sharma's status cell as dropdown with 'Active', 'On Leave', 'Contractor', 'Terminated'."""
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

    # Find Priya Sharma's row
    priya_row = None
    for cell_key, cell_data in cells.items():
        if not cell_key.startswith("A"):
            continue
        value = str(cell_data.get("value", ""))
        if value == "Priya Sharma":
            row_str = cell_key[1:]
            try:
                priya_row = int(row_str)
            except ValueError:
                continue
            break

    if priya_row is None:
        return False, "Could not find 'Priya Sharma' in column A of the Employees sheet."

    # Check cell G in Priya's row (Status column)
    status_cell_key = f"G{priya_row}"
    if status_cell_key not in cells:
        return False, f"Cell {status_cell_key} does not exist on the Employees sheet."

    status_cell = cells[status_cell_key]
    validation = status_cell.get("validation", {})

    if not validation:
        return False, f"No data validation found on cell {status_cell_key}. Cell data: {status_cell}"

    val_type = validation.get("type", "")
    if val_type != "list":
        return False, f"Data validation type is '{val_type}', expected 'list'."

    val_values = validation.get("values", "")
    if isinstance(val_values, list):
        actual = set(val_values)
    else:
        actual = set(v.strip() for v in str(val_values).split(","))

    expected = {"Active", "On Leave", "Contractor", "Terminated"}
    missing = expected - actual
    if missing:
        return False, f"Data validation is missing options: {missing}. Found: {val_values}"

    return True, f"Cell {status_cell_key} has list validation with all required options: {val_values}."
