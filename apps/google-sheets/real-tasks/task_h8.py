import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Inventory sheet (originally index 2)
    sheets = state.get("sheets", [])
    inv_sheet = None
    for s in sheets:
        if s.get("name", "").lower() in ("inventory", "stock management"):
            inv_sheet = s
            break
    if inv_sheet is None and len(sheets) > 2:
        inv_sheet = sheets[2]
    if inv_sheet is None:
        return False, "Inventory sheet not found."

    cf_rules = inv_sheet.get("conditionalFormats", [])

    if len(cf_rules) < 3:
        errors.append(f"Expected at least 3 conditional format rules, found {len(cf_rules)}")

    # Check for greater_than 100, bg #c6efce (green)
    found_gt_100 = False
    for rule in cf_rules:
        rule_type = str(rule.get("type", "")).lower()
        rule_value = str(rule.get("value", "")).strip()
        rule_bg = str(rule.get("backgroundColor", rule.get("bg", rule.get("color", "")))).lower()

        if "greater" in rule_type and rule_value == "100":
            if "#c6efce" in rule_bg or "c6efce" in rule_bg:
                found_gt_100 = True
            else:
                errors.append(f"CF greater_than 100 found but bg is '{rule_bg}', expected '#c6efce'")
                found_gt_100 = True

    if not found_gt_100:
        errors.append("No conditional format rule for greater_than 100 with background #c6efce")

    # Check for less_than 20, bg #ffc7ce (light red)
    found_lt_20 = False
    for rule in cf_rules:
        rule_type = str(rule.get("type", "")).lower()
        rule_value = str(rule.get("value", "")).strip()
        rule_bg = str(rule.get("backgroundColor", rule.get("bg", rule.get("color", "")))).lower()

        if "less" in rule_type and rule_value == "20":
            if "#ffc7ce" in rule_bg or "ffc7ce" in rule_bg:
                found_lt_20 = True
            else:
                errors.append(f"CF less_than 20 found but bg is '{rule_bg}', expected '#ffc7ce'")
                found_lt_20 = True

    if not found_lt_20:
        errors.append("No conditional format rule for less_than 20 with background #ffc7ce")

    # Check for equal_to 0, bg #ff0000 (red)
    found_eq_0 = False
    for rule in cf_rules:
        rule_type = str(rule.get("type", "")).lower()
        rule_value = str(rule.get("value", "")).strip()
        rule_bg = str(rule.get("backgroundColor", rule.get("bg", rule.get("color", "")))).lower()

        if "equal" in rule_type and rule_value == "0":
            if "#ff0000" in rule_bg or "ff0000" in rule_bg:
                found_eq_0 = True
            else:
                errors.append(f"CF equal_to 0 found but bg is '{rule_bg}', expected '#ff0000'")
                found_eq_0 = True

    if not found_eq_0:
        errors.append("No conditional format rule for equal_to 0 with background #ff0000")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
