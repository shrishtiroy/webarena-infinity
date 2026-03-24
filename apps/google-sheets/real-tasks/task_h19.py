import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    salary_sheet = None
    for sheet in sheets:
        if sheet.get("name") == "Salary Analysis":
            salary_sheet = sheet
            break

    if salary_sheet is None:
        return False, "Sheet named 'Salary Analysis' not found."

    cells = salary_sheet.get("cells", {})

    # Check 1: D column values (D2:D26) sorted descending by salary
    d_values = []
    for row in range(2, 27):
        cell_key = f"D{row}"
        cell = cells.get(cell_key)
        if cell is not None:
            val = cell.get("value", "")
            try:
                d_values.append(float(val))
            except (ValueError, TypeError):
                pass

    if len(d_values) < 2:
        errors.append(
            f"Not enough numeric values in D column to verify sort (found {len(d_values)})"
        )
    else:
        for i in range(len(d_values) - 1):
            if d_values[i] < d_values[i + 1]:
                errors.append(
                    f"D column not sorted descending: value {d_values[i]} at position {i} "
                    f"is less than {d_values[i + 1]} at position {i + 1}"
                )
                break

    # Check 2: Conditional formatting rule less_than 70000 bg #ffc7ce
    cf_rules = salary_sheet.get("conditionalFormats", [])
    found_cf = False
    for rule in cf_rules:
        rule_type = rule.get("type", "")
        threshold = rule.get("value", rule.get("threshold", ""))
        bg = rule.get("backgroundColor", rule.get("format", {}).get("backgroundColor", ""))
        try:
            threshold_num = float(threshold)
        except (ValueError, TypeError):
            threshold_num = None

        if rule_type == "less_than" and threshold_num == 70000 and bg.lower() == "#ffc7ce":
            found_cf = True
            break

    if not found_cf:
        errors.append(
            "No conditional format rule found with type 'less_than', value 70000, "
            "and backgroundColor '#ffc7ce'"
        )

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
