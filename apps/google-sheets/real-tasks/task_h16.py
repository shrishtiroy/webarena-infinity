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

    # Check 1: E column values (E2:E41) should be sorted descending
    e_values = []
    for row in range(2, 42):
        cell_key = f"E{row}"
        cell = cells.get(cell_key)
        if cell is not None:
            val = cell.get("value", "")
            try:
                e_values.append(float(val))
            except (ValueError, TypeError):
                pass

    if len(e_values) < 2:
        errors.append(f"Not enough numeric values in E column to verify sort (found {len(e_values)})")
    else:
        for i in range(len(e_values) - 1):
            if e_values[i] < e_values[i + 1]:
                errors.append(
                    f"E column not sorted descending: value {e_values[i]} at position {i} "
                    f"is less than {e_values[i + 1]} at position {i + 1}"
                )
                break

    # Check 2: frozenRows == 1
    frozen_rows = sales.get("frozenRows", 0)
    if frozen_rows != 1:
        errors.append(f"Sales frozenRows is {frozen_rows}, expected 1")

    # Check 3: Conditional formatting rule for totals >5000 green
    cf_rules = sales.get("conditionalFormats", [])
    found_cf = False
    for rule in cf_rules:
        rule_type = rule.get("type", "")
        threshold = rule.get("value", rule.get("threshold", ""))
        bg = rule.get("backgroundColor", rule.get("format", {}).get("backgroundColor", ""))
        try:
            threshold_num = float(threshold)
        except (ValueError, TypeError):
            threshold_num = None

        if rule_type == "greater_than" and threshold_num == 5000 and bg.lower() == "#c6efce":
            found_cf = True
            break

    if not found_cf:
        errors.append(
            "No conditional format rule found with type 'greater_than', value 5000, "
            "and backgroundColor '#c6efce'"
        )

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
