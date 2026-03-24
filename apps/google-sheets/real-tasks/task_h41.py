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

    for r in range(2, 32):
        d_cell = cells.get(f"D{r}")
        e_cell = cells.get(f"E{r}")
        b_cell = cells.get(f"B{r}")
        if not d_cell or not e_cell or not b_cell:
            continue

        stock = d_cell.get("value", 0)
        reorder = e_cell.get("value", 0)
        if not isinstance(stock, (int, float)) or not isinstance(reorder, (int, float)):
            continue

        b_fmt = b_cell.get("format", {})
        d_fmt = d_cell.get("format", {})
        product = b_cell.get("value", "")

        if stock == 0:
            if str(b_fmt.get("fontColor", "")).lower() != "#ff0000":
                errors.append(f"B{r} ({product}) out-of-stock: expected red text, got '{b_fmt.get('fontColor', '')}'")
            if not b_fmt.get("strikethrough"):
                errors.append(f"B{r} ({product}) out-of-stock: expected strikethrough")
        elif stock < reorder:
            if not b_fmt.get("bold"):
                errors.append(f"B{r} ({product}) below reorder: expected bold")
            if str(d_fmt.get("backgroundColor", "")).lower() != "#fce5cd":
                errors.append(f"D{r} ({product}) below reorder: expected orange bg, got '{d_fmt.get('backgroundColor', '')}'")
        elif stock > 100:
            if not b_fmt.get("italic"):
                errors.append(f"B{r} ({product}) above 100: expected italic")
            if str(d_fmt.get("backgroundColor", "")).lower() != "#c6efce":
                errors.append(f"D{r} ({product}) above 100: expected green bg, got '{d_fmt.get('backgroundColor', '')}'")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "All stock-based formatting applied correctly."
