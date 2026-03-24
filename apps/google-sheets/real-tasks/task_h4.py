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

    # Check 1: frozenRows == 1
    frozen_rows = inv_sheet.get("frozenRows", 0)
    if frozen_rows != 1:
        errors.append(f"frozenRows should be 1, got {frozen_rows}")

    # Check 2: filterMode == True
    filter_mode = inv_sheet.get("filterMode", False)
    if not filter_mode:
        errors.append("filterMode should be True")

    # Check 3: CF rule for stock < 20 with red bg #ffc7ce
    cf_rules = inv_sheet.get("conditionalFormats", [])
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

    # Check 4: Pie chart with title "Stock Distribution"
    charts = inv_sheet.get("charts", [])
    found_pie_chart = False
    for chart in charts:
        chart_type = str(chart.get("type", "")).lower()
        chart_title = str(chart.get("title", "")).strip()
        if chart_type == "pie" and chart_title == "Stock Distribution":
            found_pie_chart = True
            break

    if not found_pie_chart:
        errors.append("No pie chart with title 'Stock Distribution' found on Inventory sheet")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
