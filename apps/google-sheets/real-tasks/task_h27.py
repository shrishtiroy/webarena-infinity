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

    found_returning = False
    found_vendor = False

    for r in range(2, 27):
        g_cell = cells.get(f"G{r}", {})
        val = g_cell.get("value", "")
        fmt = g_cell.get("format", {})
        bg = fmt.get("backgroundColor", "").lower()

        if val == "On Leave":
            errors.append(f"G{r} still has 'On Leave' (should be 'Returning')")
        if val == "Contractor":
            errors.append(f"G{r} still has 'Contractor' (should be 'Vendor')")

        if val == "Returning":
            found_returning = True
            if bg != "#cfe2f3":
                errors.append(f"G{r} 'Returning' bg should be '#cfe2f3', got '{bg}'")

        if val == "Vendor":
            found_vendor = True
            if bg != "#fce5cd":
                errors.append(f"G{r} 'Vendor' bg should be '#fce5cd', got '{bg}'")

    if not found_returning:
        errors.append("No 'Returning' status found (expected from 'On Leave' employees)")
    if not found_vendor:
        errors.append("No 'Vendor' status found (expected from 'Contractor' employees)")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
