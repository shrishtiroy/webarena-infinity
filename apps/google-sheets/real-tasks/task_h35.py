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

    expected_options = "Active,On Leave,Contractor,Terminated,Remote"

    # Check validation and underline on G2:G26
    missing_validation = []
    missing_underline = []
    for r in range(2, 27):
        g_cell = cells.get(f"G{r}", {})
        validation = g_cell.get("validation")
        if not validation:
            missing_validation.append(f"G{r}")
        elif validation.get("type") != "list":
            missing_validation.append(f"G{r} (type={validation.get('type')})")
        elif validation.get("values") != expected_options:
            missing_validation.append(
                f"G{r} (values='{validation.get('values')}')"
            )

        fmt = g_cell.get("format", {})
        if not fmt.get("underline"):
            missing_underline.append(f"G{r}")

    if missing_validation:
        sample = ", ".join(missing_validation[:3])
        errors.append(
            f"Missing/incorrect data validation on: {sample}"
            + (f" ... and {len(missing_validation)-3} more" if len(missing_validation) > 3 else "")
        )

    if missing_underline:
        sample = ", ".join(missing_underline[:3])
        errors.append(
            f"Missing underline on: {sample}"
            + (f" ... and {len(missing_underline)-3} more" if len(missing_underline) > 3 else "")
        )

    # Check named range
    named_ranges = state.get("namedRanges", {})
    sc = named_ranges.get("StatusColumn")
    if sc is None:
        errors.append("Named range 'StatusColumn' not found")
    elif sc != "Employees!G2:G26":
        errors.append(f"StatusColumn should be 'Employees!G2:G26', got '{sc}'")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
