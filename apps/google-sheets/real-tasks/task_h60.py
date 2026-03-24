import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])

    # Find original Inventory to know reorder levels
    inv = None
    for s in sheets:
        if s.get("name", "") in ("Inventory", "Stock Management"):
            inv = s
            break

    # Find Restocking Plan sheet
    rp = None
    for s in sheets:
        if s.get("name", "").strip() == "Restocking Plan":
            rp = s
            break
    if rp is None:
        return False, f"No sheet named 'Restocking Plan' found. Sheets: {[s['name'] for s in sheets]}"

    rp_cells = rp.get("cells", {})

    # Check sorted by stock (column D) ascending
    prev_val = None
    for r in range(2, 32):
        d_cell = rp_cells.get(f"D{r}")
        if d_cell and isinstance(d_cell.get("value"), (int, float)):
            val = d_cell["value"]
            if prev_val is not None and val < prev_val - 0.01:
                errors.append(f"D{r} ({val}) < D{r-1} ({prev_val}): not sorted ascending")
                break
            prev_val = val

    # Check frozen rows
    if rp.get("frozenRows", 0) < 1:
        errors.append("Header row should be frozen")

    # Check formatting based on stock vs reorder
    for r in range(2, 32):
        d_cell = rp_cells.get(f"D{r}")
        e_cell = rp_cells.get(f"E{r}")
        b_cell = rp_cells.get(f"B{r}")
        if not d_cell or not e_cell or not b_cell:
            continue

        stock = d_cell.get("value", 0)
        reorder = e_cell.get("value", 0)
        if not isinstance(stock, (int, float)) or not isinstance(reorder, (int, float)):
            continue

        d_fmt = d_cell.get("format", {})
        if stock < reorder:
            # Below reorder: bold name + red stock bg
            if not b_cell.get("format", {}).get("bold"):
                errors.append(f"B{r} (stock {stock} < reorder {reorder}) should be bold")
            bg = str(d_fmt.get("backgroundColor", "")).lower()
            if bg != "#ffc7ce":
                errors.append(f"D{r} (below reorder) bg should be '#ffc7ce', got '{bg}'")
        elif stock > 100:
            # Above 100: green stock bg
            bg = str(d_fmt.get("backgroundColor", "")).lower()
            if bg != "#c6efce":
                errors.append(f"D{r} (stock {stock} > 100) bg should be '#c6efce', got '{bg}'")

    # Check named range
    named = state.get("namedRanges", {})
    if "RestockPlan" not in named:
        errors.append("Named range 'RestockPlan' not found")
    elif "'Restocking Plan'!B2:E31" not in named["RestockPlan"]:
        # Be flexible about quoting
        val = named["RestockPlan"]
        if "Restocking Plan" not in val or "B2:E31" not in val:
            errors.append(f"RestockPlan should reference 'Restocking Plan'!B2:E31, got '{val}'")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "Restocking Plan sheet created with sorting and formatting."
