import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    inv = None
    for s in sheets:
        if s.get("name", "") in ("Inventory", "Stock Management"):
            inv = s
            break
    if inv is None and len(sheets) > 2:
        inv = sheets[2]
    if inv is None:
        return False, "Inventory sheet not found."

    cf_rules = inv.get("conditionalFormats", [])

    # Check 4 CF rules
    checks = {
        "equal_to_0_red": False,
        "between_1_10_orange": False,
        "between_11_19_yellow": False,
        "above_100_green": False,
    }

    for rule in cf_rules:
        rtype = rule.get("type", "")
        bg = rule.get("backgroundColor", "").lower()
        val = str(rule.get("value", ""))
        val2 = str(rule.get("value2", ""))

        if rtype == "equal_to" and val == "0" and bg == "#ff0000":
            checks["equal_to_0_red"] = True
        if rtype == "between" and val == "1" and val2 == "10" and bg == "#fce5cd":
            checks["between_1_10_orange"] = True
        if rtype == "between" and val == "11" and val2 == "19" and bg == "#ffff00":
            checks["between_11_19_yellow"] = True
        if rtype == "greater_than" and val == "100" and bg == "#c6efce":
            checks["above_100_green"] = True

    for desc, found in checks.items():
        if not found:
            errors.append(f"Missing CF rule: {desc}")

    # Check named range
    named_ranges = state.get("namedRanges", {})
    sl = named_ranges.get("StockLevels")
    if sl is None:
        errors.append("Named range 'StockLevels' not found")
    elif sl != "Inventory!D2:D31":
        errors.append(f"StockLevels should be 'Inventory!D2:D31', got '{sl}'")

    # Check frozen
    if inv.get("frozenRows", 0) < 1:
        errors.append("Header row should be frozen")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
