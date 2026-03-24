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

    # Check data validation on dept cells
    expected_options = "Engineering,Sales,Marketing,HR,Finance,Operations"
    for r in range(2, 27):
        b_cell = cells.get(f"B{r}")
        if b_cell:
            val = b_cell.get("validation", {})
            if val.get("type") != "list":
                errors.append(f"B{r} should have list validation")
                break
            elif val.get("values") != expected_options:
                errors.append(f"B{r} validation should be '{expected_options}'")
                break

    # Check merge A27:B27
    merged = emp.get("mergedCells", [])
    if "A27:B27" not in merged:
        errors.append("A27:B27 should be merged")

    # Check A27 label
    a27 = cells.get("A27", {})
    if str(a27.get("value", "")).strip() != "Department Count":
        errors.append(f"A27 should be 'Department Count', got '{a27.get('value', '')}'")
    if not a27.get("format", {}).get("bold"):
        errors.append("A27 should be bold")

    # Check C27 formula
    c27 = cells.get("C27", {})
    formula = str(c27.get("formula", "")).upper()
    if "COUNTA" not in formula:
        errors.append(f"C27 should have COUNTA formula, got '{c27.get('formula', '')}'")

    # Check dept cells italic
    for r in range(2, 27):
        b_cell = cells.get(f"B{r}")
        if b_cell and not b_cell.get("format", {}).get("italic"):
            errors.append(f"B{r} should be italic")
            break

    # Check named range
    named = state.get("namedRanges", {})
    if "DeptColumn" not in named:
        errors.append("Named range 'DeptColumn' not found")
    elif named["DeptColumn"] != "Employees!B2:B26":
        errors.append(f"DeptColumn should be 'Employees!B2:B26', got '{named['DeptColumn']}'")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "Department validation, merge, formula, italic, and named range all correct."
