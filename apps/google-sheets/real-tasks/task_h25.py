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

    # Find the two Docking Station rows by scanning product names
    docking_rows = []
    for r in range(2, 32):
        b_cell = cells.get(f"B{r}")
        if b_cell and "Docking Station" in str(b_cell.get("value", "")):
            f_cell = cells.get(f"F{r}", {})
            cost = f_cell.get("value", 0)
            docking_rows.append((r, cost))

    if len(docking_rows) < 2:
        return False, f"Expected 2 Docking Station products, found {len(docking_rows)}"

    # Sort by cost to identify cheaper vs more expensive
    docking_rows.sort(key=lambda x: x[1])
    cheap_row = docking_rows[0][0]
    expensive_row = docking_rows[-1][0]

    # Expensive one: stock=25, bold product name
    d_exp = cells.get(f"D{expensive_row}", {})
    if d_exp.get("value") != 25 and str(d_exp.get("value", "")) != "25":
        errors.append(
            f"D{expensive_row} (expensive Docking Station) stock should be 25, "
            f"got '{d_exp.get('value', '')}'"
        )

    b_exp = cells.get(f"B{expensive_row}", {})
    if not b_exp.get("format", {}).get("bold"):
        errors.append(f"B{expensive_row} (expensive Docking Station) should be bold")

    # Cheaper one: italic + strikethrough
    b_cheap = cells.get(f"B{cheap_row}", {})
    cheap_fmt = b_cheap.get("format", {})
    if not cheap_fmt.get("italic"):
        errors.append(f"B{cheap_row} (cheaper Docking Station) should be italic")
    if not cheap_fmt.get("strikethrough"):
        errors.append(f"B{cheap_row} (cheaper Docking Station) should have strikethrough")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
