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

    # Find two Laptop rows
    laptop_rows = []
    for r in range(2, 32):
        b_cell = cells.get(f"B{r}")
        if b_cell and "Laptop" in str(b_cell.get("value", "")) and "Bag" not in str(b_cell.get("value", "")) and "Stand" not in str(b_cell.get("value", "")):
            d_cell = cells.get(f"D{r}", {})
            stock = d_cell.get("value", 0)
            laptop_rows.append((r, stock))

    if len(laptop_rows) < 2:
        return False, f"Expected 2 Laptop products, found {len(laptop_rows)}"

    laptop_rows.sort(key=lambda x: x[1])
    low_row = laptop_rows[0][0]
    high_row = laptop_rows[-1][0]

    # Higher stock: bold name + green stock bg
    b_high = cells.get(f"B{high_row}", {})
    if not b_high.get("format", {}).get("bold"):
        errors.append(f"B{high_row} (higher stock Laptop) should be bold")
    d_high = cells.get(f"D{high_row}", {})
    bg = str(d_high.get("format", {}).get("backgroundColor", "")).lower()
    if bg != "#c6efce":
        errors.append(f"D{high_row} (higher stock) bg should be '#c6efce', got '{bg}'")

    # Lower stock: underline name + reorder=25 + orange stock bg
    b_low = cells.get(f"B{low_row}", {})
    if not b_low.get("format", {}).get("underline"):
        errors.append(f"B{low_row} (lower stock Laptop) should be underlined")
    e_low = cells.get(f"E{low_row}", {})
    e_val = e_low.get("value")
    if e_val != 25 and str(e_val) != "25":
        errors.append(f"E{low_row} reorder should be 25, got '{e_val}'")
    d_low = cells.get(f"D{low_row}", {})
    bg_low = str(d_low.get("format", {}).get("backgroundColor", "")).lower()
    if bg_low != "#fce5cd":
        errors.append(f"D{low_row} (lower stock) bg should be '#fce5cd', got '{bg_low}'")

    if errors:
        return False, "; ".join(errors)
    return True, "Laptop products disambiguated and formatted correctly."
