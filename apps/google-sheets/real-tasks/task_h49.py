import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])

    # Get Inventory data to compute expected items
    inv = None
    for s in sheets:
        if s.get("name", "") in ("Inventory", "Stock Management"):
            inv = s
            break
    if inv is None:
        # Try to find by checking for reorder report data
        pass

    # Find Reorder Report sheet
    rr = None
    for s in sheets:
        if s.get("name", "").strip() == "Reorder Report":
            rr = s
            break
    if rr is None:
        return False, f"No sheet named 'Reorder Report' found. Sheets: {[s['name'] for s in sheets]}"

    rr_cells = rr.get("cells", {})

    # Check headers
    for col, header in [("A", "Product"), ("B", "Current Stock"), ("C", "Reorder Level"), ("D", "Shortage")]:
        cell = rr_cells.get(f"{col}1", {})
        if str(cell.get("value", "")).strip() != header:
            errors.append(f"{col}1 should be '{header}', got '{cell.get('value', '')}'")
        fmt = cell.get("format", {})
        if not fmt.get("bold"):
            errors.append(f"{col}1 should be bold")
        if str(fmt.get("backgroundColor", "")).lower() != "#ffc7ce":
            errors.append(f"{col}1 bg should be '#ffc7ce'")

    # Compute expected items from Inventory
    if inv:
        inv_cells = inv.get("cells", {})
        below_reorder = []
        for r in range(2, 32):
            b_cell = inv_cells.get(f"B{r}")
            d_cell = inv_cells.get(f"D{r}")
            e_cell = inv_cells.get(f"E{r}")
            if b_cell and d_cell and e_cell:
                stock = d_cell.get("value", 0)
                reorder = e_cell.get("value", 0)
                if isinstance(stock, (int, float)) and isinstance(reorder, (int, float)):
                    if stock < reorder:
                        product = str(b_cell.get("value", ""))
                        shortage = reorder - stock
                        below_reorder.append((product, stock, reorder, shortage))

        # Should be sorted by shortage desc
        below_reorder.sort(key=lambda x: x[3], reverse=True)

        if len(below_reorder) == 0:
            errors.append("No items below reorder level found in Inventory")
        else:
            for i, (product, stock, reorder, shortage) in enumerate(below_reorder):
                row = i + 2
                a_val = str(rr_cells.get(f"A{row}", {}).get("value", "")).strip()
                if a_val != product:
                    errors.append(f"A{row} should be '{product}', got '{a_val}'")
                d_val = rr_cells.get(f"D{row}", {}).get("value")
                if isinstance(d_val, (int, float)):
                    if abs(d_val - shortage) > 0.01:
                        errors.append(f"D{row} shortage should be {shortage}, got {d_val}")
                else:
                    errors.append(f"D{row} should be numeric, got '{d_val}'")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "Reorder Report created correctly."
