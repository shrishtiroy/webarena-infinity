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

    # Check data validation on all status cells
    expected_options = "Active,On Leave,Remote,Contractor,Terminated"
    for r in range(2, 27):
        g_cell = cells.get(f"G{r}")
        if g_cell:
            val = g_cell.get("validation", {})
            if val.get("type") != "list":
                errors.append(f"G{r} should have list validation")
            elif val.get("values") != expected_options:
                errors.append(f"G{r} validation values should be '{expected_options}'")

    # Check Contractor -> Remote
    for r in range(2, 27):
        g_cell = cells.get(f"G{r}")
        if g_cell and str(g_cell.get("value", "")) == "Contractor":
            errors.append(f"G{r} still has 'Contractor', should be 'Remote'")

    # Check CF rules
    cf = emp.get("conditionalFormats", [])
    found_on_leave = False
    found_remote = False
    for rule in cf:
        rng = rule.get("range", "")
        if "G" in rng:
            if rule.get("type") == "text_contains" and rule.get("value") == "On Leave":
                if str(rule.get("backgroundColor", "")).lower() == "#ffff00":
                    found_on_leave = True
            if rule.get("type") == "text_contains" and rule.get("value") == "Remote":
                if str(rule.get("backgroundColor", "")).lower() == "#cfe2f3":
                    found_remote = True
    if not found_on_leave:
        errors.append("Missing CF: 'On Leave' with yellow bg")
    if not found_remote:
        errors.append("Missing CF: 'Remote' with light blue bg")

    # Check named range
    named = state.get("namedRanges", {})
    if "EmployeeStatus" not in named:
        errors.append("Named range 'EmployeeStatus' not found")
    elif named["EmployeeStatus"] != "Employees!G2:G26":
        errors.append(f"EmployeeStatus should be 'Employees!G2:G26', got '{named['EmployeeStatus']}'")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "Status validation, replacement, CF, and named range all correct."
