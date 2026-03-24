import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    sales = None
    for s in sheets:
        if s.get("name", "") in ("Sales", "Revenue", "Revenue Data"):
            sales = s
            break
    if sales is None:
        sales = sheets[0]

    cells = sales.get("cells", {})

    # Check merge
    merged = sales.get("mergedCells", [])
    if "A44:D44" not in merged:
        errors.append("Cells A44:D44 should be merged")

    # Check A44 label
    a44 = cells.get("A44", {})
    if str(a44.get("value", "")).strip() != "Performance Summary":
        errors.append(
            f"A44 should be 'Performance Summary', got '{a44.get('value', '')}'"
        )
    fmt_a44 = a44.get("format", {})
    if not fmt_a44.get("bold"):
        errors.append("A44 should be bold")
    if fmt_a44.get("horizontalAlign") != "center":
        errors.append("A44 should be centered")

    # Check E44: MIN formula
    e44 = cells.get("E44", {})
    formula_e = str(e44.get("formula", "")).upper()
    if "MIN" not in formula_e:
        errors.append(f"E44 should have MIN formula, got '{e44.get('formula', '')}'")

    # Check F44: MAX formula, currency
    f44 = cells.get("F44", {})
    formula_f = str(f44.get("formula", "")).upper()
    if "MAX" not in formula_f:
        errors.append(f"F44 should have MAX formula, got '{f44.get('formula', '')}'")
    if str(f44.get("format", {}).get("numberFormat", "")).lower() != "currency":
        errors.append("F44 should be formatted as currency")

    # Check G44: SUM formula, currency
    g44 = cells.get("G44", {})
    formula_g = str(g44.get("formula", "")).upper()
    if "SUM" not in formula_g:
        errors.append(f"G44 should have SUM formula, got '{g44.get('formula', '')}'")
    if str(g44.get("format", {}).get("numberFormat", "")).lower() != "currency":
        errors.append("G44 should be formatted as currency")

    # Check CF rule on G2:G41 > 10000 green
    cf_rules = sales.get("conditionalFormats", [])
    found_cf = False
    for rule in cf_rules:
        if (rule.get("type") == "greater_than"
                and str(rule.get("value", "")) == "10000"
                and rule.get("backgroundColor", "").lower() == "#c6efce"):
            found_cf = True
            break
    if not found_cf:
        errors.append(
            "No CF rule found: greater_than 10000 with bg '#c6efce'"
        )

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
