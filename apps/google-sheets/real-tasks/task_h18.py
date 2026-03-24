import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    if len(sheets) < 1:
        return False, "No sheets found in state."

    sales = sheets[0]
    cells = sales.get("cells", {})
    merged_cells = sales.get("mergedCells", [])

    # Check 1: A44:D44 in mergedCells
    if "A44:D44" not in merged_cells:
        errors.append(f"'A44:D44' not found in mergedCells (found: {merged_cells})")

    # Check 2: A44 value == "Summary Statistics" and bold
    a44 = cells.get("A44")
    if a44 is None:
        errors.append("Cell A44 is missing")
    else:
        value = a44.get("value", "")
        if value != "Summary Statistics":
            errors.append(f"A44 value is '{value}', expected 'Summary Statistics'")
        fmt = a44.get("format", {})
        if not fmt.get("bold"):
            errors.append("A44 is not bold")

    # Check 3: E44 has COUNT formula
    e44 = cells.get("E44")
    if e44 is None:
        errors.append("Cell E44 is missing")
    else:
        formula = e44.get("formula", "")
        if "COUNT" not in formula.upper():
            errors.append(f"E44 formula is '{formula}', expected a COUNT formula")

    # Check 4: F44 has AVERAGE formula
    f44 = cells.get("F44")
    if f44 is None:
        errors.append("Cell F44 is missing")
    else:
        formula = f44.get("formula", "")
        if "AVERAGE" not in formula.upper():
            errors.append(f"F44 formula is '{formula}', expected an AVERAGE formula")

    # Check 5: G44 has MAX formula
    g44 = cells.get("G44")
    if g44 is None:
        errors.append("Cell G44 is missing")
    else:
        formula = g44.get("formula", "")
        if "MAX" not in formula.upper():
            errors.append(f"G44 formula is '{formula}', expected a MAX formula")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
