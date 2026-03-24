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

    # Find two Keyboard rows
    keyboard_rows = []
    for r in range(2, 32):
        b_cell = cells.get(f"B{r}")
        if b_cell and "Keyboard" in str(b_cell.get("value", "")):
            d_cell = cells.get(f"D{r}", {})
            stock = d_cell.get("value", 0)
            keyboard_rows.append((r, stock))

    if len(keyboard_rows) < 2:
        return False, f"Expected 2 Keyboard products, found {len(keyboard_rows)}"

    keyboard_rows.sort(key=lambda x: x[1])
    low_row = keyboard_rows[0][0]
    high_row = keyboard_rows[-1][0]

    # Higher stock: bold name + green unit cost bg
    b_high = cells.get(f"B{high_row}", {})
    if not b_high.get("format", {}).get("bold"):
        errors.append(f"B{high_row} (higher stock Keyboard) should be bold")
    f_high = cells.get(f"F{high_row}", {})
    bg = str(f_high.get("format", {}).get("backgroundColor", "")).lower()
    if bg != "#c6efce":
        errors.append(f"F{high_row} (higher stock) bg should be '#c6efce', got '{bg}'")

    # Lower stock: italic name + reorder=25 + red unit cost bg
    b_low = cells.get(f"B{low_row}", {})
    if not b_low.get("format", {}).get("italic"):
        errors.append(f"B{low_row} (lower stock Keyboard) should be italic")
    e_low = cells.get(f"E{low_row}", {})
    e_val = e_low.get("value")
    if e_val != 25 and str(e_val) != "25":
        errors.append(f"E{low_row} reorder should be 25, got '{e_val}'")
    f_low = cells.get(f"F{low_row}", {})
    bg_low = str(f_low.get("format", {}).get("backgroundColor", "")).lower()
    if bg_low != "#ffc7ce":
        errors.append(f"F{low_row} (lower stock) bg should be '#ffc7ce', got '{bg_low}'")

    if errors:
        return False, "; ".join(errors)
    return True, "Keyboard products disambiguated and formatted correctly."
