import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    if len(sheets) < 2:
        return False, "Employees sheet (index 1) not found."

    employees = sheets[1]
    cells = employees.get("cells", {})

    # Check 1: D27 has SUM formula, bold, currency format
    d27 = cells.get("D27")
    if d27 is None:
        errors.append("Cell D27 is missing")
    else:
        formula = d27.get("formula", "")
        if "SUM" not in formula.upper() or "D2" not in formula.upper() or "D26" not in formula.upper():
            errors.append(
                f"D27 formula is '{formula}', expected a SUM formula referencing D2:D26"
            )

        fmt = d27.get("format", {})
        if not fmt.get("bold"):
            errors.append("D27 is not bold")

        number_format = fmt.get("numberFormat", "")
        # Accept common currency format indicators
        is_currency = any(
            indicator in str(number_format).lower()
            for indicator in ["currency", "dollar", "$", "usd"]
        )
        if not is_currency:
            errors.append(
                f"D27 numberFormat is '{number_format}', expected a currency format"
            )

    # Check 2: Conditional formatting rule greater_than 130000 bg #c6efce
    cf_rules = employees.get("conditionalFormats", [])
    found_cf = False
    for rule in cf_rules:
        rule_type = rule.get("type", "")
        threshold = rule.get("value", rule.get("threshold", ""))
        bg = rule.get("backgroundColor", rule.get("format", {}).get("backgroundColor", ""))
        try:
            threshold_num = float(threshold)
        except (ValueError, TypeError):
            threshold_num = None

        if rule_type == "greater_than" and threshold_num == 130000 and bg.lower() == "#c6efce":
            found_cf = True
            break

    if not found_cf:
        errors.append(
            "No conditional format rule found with type 'greater_than', value 130000, "
            "and backgroundColor '#c6efce'"
        )

    # Check 3: frozenRows == 1
    frozen_rows = employees.get("frozenRows", 0)
    if frozen_rows != 1:
        errors.append(f"Employees frozenRows is {frozen_rows}, expected 1")

    # Check 4: frozenCols == 1
    frozen_cols = employees.get("frozenCols", 0)
    if frozen_cols != 1:
        errors.append(f"Employees frozenCols is {frozen_cols}, expected 1")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
