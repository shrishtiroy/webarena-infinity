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

    # Check frozen
    if emp.get("frozenRows", 0) < 1:
        errors.append("Header row should be frozen (frozenRows >= 1)")
    if emp.get("frozenCols", 0) < 1:
        errors.append("First column should be frozen (frozenCols >= 1)")

    # Check H1 header
    h1 = cells.get("H1", {})
    if str(h1.get("value", "")).strip() != "Rank":
        errors.append(f"H1 should be 'Rank', got '{h1.get('value', '')}'")
    if not h1.get("format", {}).get("bold"):
        errors.append("H1 should be bold")

    # Check sorted by salary descending
    prev_salary = None
    for r in range(2, 27):
        d_cell = cells.get(f"D{r}")
        if d_cell and isinstance(d_cell.get("value"), (int, float)):
            sal = d_cell["value"]
            if prev_salary is not None and sal > prev_salary:
                errors.append(
                    f"Not sorted desc: D{r} ({sal}) > D{r-1} ({prev_salary})"
                )
                break
            prev_salary = sal

    # Check rank numbers H2:H26
    for r in range(2, 27):
        h_cell = cells.get(f"H{r}", {})
        expected_rank = r - 1
        actual = h_cell.get("value")
        if actual != expected_rank and str(actual) != str(expected_rank):
            errors.append(f"H{r} should be {expected_rank}, got '{actual}'")
            if len(errors) > 5:
                errors.append("... (truncated)")
                break

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
