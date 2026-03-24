import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Task: Make Priya Sharma's name bold, italic, and underlined."""
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

    # Find Priya Sharma in column A
    priya_cell_key = None
    for cell_key, cell_data in cells.items():
        if not cell_key.startswith("A"):
            continue
        value = str(cell_data.get("value", ""))
        if value == "Priya Sharma":
            priya_cell_key = cell_key
            break

    if priya_cell_key is None:
        return False, "Could not find 'Priya Sharma' in column A of the Employees sheet."

    cell = cells[priya_cell_key]
    fmt = cell.get("format", {})

    is_bold = fmt.get("bold", False) is True
    is_italic = fmt.get("italic", False) is True
    is_underline = fmt.get("underline", False) is True

    missing = []
    if not is_bold:
        missing.append("bold")
    if not is_italic:
        missing.append("italic")
    if not is_underline:
        missing.append("underline")

    if missing:
        return False, f"Priya Sharma's cell ({priya_cell_key}) is missing formatting: {', '.join(missing)}. Current format: {fmt}"

    return True, f"Priya Sharma's cell ({priya_cell_key}) is bold, italic, and underlined."
