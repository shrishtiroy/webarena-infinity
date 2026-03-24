import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Employees sheet is at index 1
    sheets = state.get("sheets", [])
    emp_sheet = None
    for s in sheets:
        if s.get("name", "").lower() in ("employees", "team directory"):
            emp_sheet = s
            break
    if emp_sheet is None and len(sheets) > 1:
        emp_sheet = sheets[1]
    if emp_sheet is None:
        return False, "Employees sheet not found."

    cells = emp_sheet.get("cells", {})

    # Check 1: B column values (rows 2-26) in ascending alphabetical order
    dept_values = []
    for row in range(2, 27):
        cell_key = f"B{row}"
        cell = cells.get(cell_key, {})
        val = str(cell.get("value", "")).strip()
        if val:
            dept_values.append(val)

    if len(dept_values) < 2:
        errors.append(f"Expected department values in B2:B26, found only {len(dept_values)}")
    else:
        sorted_values = sorted(dept_values, key=lambda x: x.lower())
        if dept_values != sorted_values:
            errors.append("Department column (B) is not sorted in ascending alphabetical order")

    # Check 2: frozenRows == 1
    frozen_rows = emp_sheet.get("frozenRows", 0)
    if frozen_rows != 1:
        errors.append(f"frozenRows should be 1, got {frozen_rows}")

    # Check 3: Conditional format for "On Leave" with yellow background
    cf_rules = emp_sheet.get("conditionalFormats", [])
    found_on_leave_cf = False
    for rule in cf_rules:
        rule_type = str(rule.get("type", "")).lower()
        rule_value = str(rule.get("value", "")).strip()
        rule_bg = str(rule.get("backgroundColor", rule.get("bg", rule.get("color", "")))).lower()

        if "text" in rule_type and "contain" in rule_type:
            if "on leave" in rule_value.lower():
                if "#ffff00" in rule_bg or "ffff00" in rule_bg or rule_bg == "yellow":
                    found_on_leave_cf = True
                else:
                    errors.append(f"On Leave CF rule found but background is '{rule_bg}', expected '#ffff00'")
                    found_on_leave_cf = True  # rule exists but wrong color

    if not found_on_leave_cf:
        errors.append("No conditional format rule found for text_contains 'On Leave' with yellow (#ffff00) background")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
