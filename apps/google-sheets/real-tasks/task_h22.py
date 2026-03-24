import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    emp = None
    for s in sheets:
        if s.get("name", "") in ("Employees", "Team Directory"):
            emp = s
            break
    if emp is None and len(sheets) > 1:
        emp = sheets[1]
    if emp is None:
        return False, "Employees sheet not found."

    cells = emp.get("cells", {})

    # Find employee with lowest salary by scanning D column
    min_salary = None
    min_row = None
    for r in range(2, 27):
        cell = cells.get(f"D{r}")
        if cell and isinstance(cell.get("value"), (int, float)):
            sal = cell["value"]
            if min_salary is None or sal < min_salary:
                min_salary = sal
                min_row = r

    if min_row is None:
        return False, "Could not find any salary data."

    # Check name cell is bold and underline
    name_cell = cells.get(f"A{min_row}", {})
    fmt = name_cell.get("format", {})
    if not fmt.get("bold"):
        errors.append(f"A{min_row} (lowest salary employee) should be bold")
    if not fmt.get("underline"):
        errors.append(f"A{min_row} (lowest salary employee) should be underlined")

    # Check salary cell bg
    sal_cell = cells.get(f"D{min_row}", {})
    sal_fmt = sal_cell.get("format", {})
    sal_bg = sal_fmt.get("backgroundColor", "")
    if sal_bg.lower() != "#ffc7ce":
        errors.append(
            f"D{min_row} background should be '#ffc7ce', got '{sal_bg}'"
        )

    # Check status is Under Review
    status_cell = cells.get(f"G{min_row}", {})
    status_val = str(status_cell.get("value", "")).strip()
    if status_val != "Under Review":
        errors.append(
            f"G{min_row} should be 'Under Review', got '{status_val}'"
        )

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
