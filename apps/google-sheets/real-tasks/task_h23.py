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

    cells = inv.get("cells", {})

    # Find rows where stock (D) < reorder level (E)
    below_reorder_rows = []
    for r in range(2, 32):
        d_cell = cells.get(f"D{r}")
        e_cell = cells.get(f"E{r}")
        if d_cell and e_cell:
            stock = d_cell.get("value")
            reorder = e_cell.get("value")
            if isinstance(stock, (int, float)) and isinstance(reorder, (int, float)):
                if stock < reorder:
                    below_reorder_rows.append(r)

    if not below_reorder_rows:
        errors.append("No items found with stock below reorder level")
    else:
        for r in below_reorder_rows:
            b_cell = cells.get(f"B{r}", {})
            fmt = b_cell.get("format", {})
            if not fmt.get("bold"):
                product = b_cell.get("value", f"row {r}")
                errors.append(f"B{r} ({product}) should be bold (stock < reorder)")

    # Check CF rule: equal_to 0, bg #cc0000, fontColor #ffffff
    cf_rules = inv.get("conditionalFormats", [])
    found_cf = False
    for rule in cf_rules:
        if (rule.get("type") == "equal_to"
                and str(rule.get("value", "")) == "0"
                and rule.get("backgroundColor", "").lower() == "#cc0000"):
            font_color = rule.get("fontColor", "")
            if font_color.lower() == "#ffffff":
                found_cf = True
                break

    if not found_cf:
        errors.append(
            "No CF rule found: equal_to 0 with bg '#cc0000' and fontColor '#ffffff'"
        )

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
