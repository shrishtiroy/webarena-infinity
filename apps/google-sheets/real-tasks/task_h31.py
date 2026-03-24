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

    # Check no "PeriphCo Supply" exists, "PeriphCo International" does
    found_old = False
    found_new = False
    for addr, cell in cells.items():
        val = str(cell.get("value", ""))
        if val == "PeriphCo Supply":
            found_old = True
        if val == "PeriphCo International":
            found_new = True

    if found_old:
        errors.append("'PeriphCo Supply' still found (should be replaced)")
    if not found_new:
        errors.append("'PeriphCo International' not found")

    # Check column H is gone (no cells in column H)
    has_h_col = False
    for addr in cells:
        if addr.startswith("H"):
            rest = addr[1:]
            if rest.isdigit():
                has_h_col = True
                break
    if has_h_col:
        errors.append("Column H still exists (Last Restocked should be deleted)")

    # Check sorted by product name (column B) ascending
    prev_name = None
    for r in range(2, 32):
        b_cell = cells.get(f"B{r}")
        if b_cell and b_cell.get("value") is not None:
            name = str(b_cell["value"]).lower()
            if prev_name is not None and name < prev_name:
                errors.append(
                    f"Not sorted alphabetically: B{r} ('{b_cell['value']}') "
                    f"< previous ('{prev_name}')"
                )
                break
            prev_name = name

    # Check frozen
    if inv.get("frozenRows", 0) < 1:
        errors.append("Header row should be frozen")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
