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

    # Check header cells have light blue bg
    for col in "ABCDEFG":
        cell = cells.get(f"{col}1", {})
        bg = str(cell.get("format", {}).get("backgroundColor", "")).lower()
        if bg != "#cfe2f3":
            errors.append(f"{col}1 bg should be '#cfe2f3', got '{bg}'")

    # Check all names bold
    for r in range(2, 27):
        a_cell = cells.get(f"A{r}")
        if a_cell and not a_cell.get("format", {}).get("bold"):
            errors.append(f"A{r} should be bold")

    # Check salaries right-aligned
    for r in range(2, 27):
        d_cell = cells.get(f"D{r}")
        if d_cell:
            align = d_cell.get("format", {}).get("horizontalAlign", "")
            if align != "right":
                errors.append(f"D{r} should be right-aligned, got '{align}'")

    # Check emails italic
    for r in range(2, 27):
        f_cell = cells.get(f"F{r}")
        if f_cell and not f_cell.get("format", {}).get("italic"):
            errors.append(f"F{r} should be italic")

    # Check CF: salary > 120000 green text
    cf = emp.get("conditionalFormats", [])
    found_cf = False
    for rule in cf:
        rng = rule.get("range", "")
        if "D" in rng:
            if rule.get("type") == "greater_than" and str(rule.get("value", "")) == "120000":
                if str(rule.get("fontColor", "")).lower() == "#006100":
                    found_cf = True
    if not found_cf:
        errors.append("Missing CF: D > 120000 with green text (#006100)")

    # Check freeze
    if emp.get("frozenRows", 0) < 1:
        errors.append("Top row should be frozen")
    if emp.get("frozenCols", 0) < 1:
        errors.append("First column should be frozen")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "Employee sheet formatting overhaul applied correctly."
