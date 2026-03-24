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
        if s.get("name", "") in ("Sales", "Revenue Data", "Revenue"):
            sales = s
            break
    if sales is None and len(sheets) > 0:
        sales = sheets[0]
    if sales is None:
        return False, "Sales sheet not found."

    cells = sales.get("cells", {})

    # Compute Q1 2024 totals (Jan-Mar)
    q1_qty = 0
    q1_rev = 0
    for r in range(2, 42):
        a_cell = cells.get(f"A{r}")
        if not a_cell:
            continue
        date_str = str(a_cell.get("value", ""))
        parts = date_str.split("/")
        if len(parts) != 3:
            continue
        try:
            month = int(parts[0])
            year = int(parts[2])
        except ValueError:
            continue
        if year == 2024 and 1 <= month <= 3:
            e_cell = cells.get(f"E{r}")
            g_cell = cells.get(f"G{r}")
            if e_cell and isinstance(e_cell.get("value"), (int, float)):
                q1_qty += e_cell["value"]
            if g_cell and isinstance(g_cell.get("value"), (int, float)):
                q1_rev += g_cell["value"]

    # Check merge
    merged = sales.get("mergedCells", [])
    if "A44:C44" not in merged:
        errors.append("A44:C44 should be merged")

    # Check A44 label
    a44 = cells.get("A44", {})
    if str(a44.get("value", "")).strip() != "Q1 2024":
        errors.append(f"A44 should be 'Q1 2024', got '{a44.get('value', '')}'")
    if not a44.get("format", {}).get("bold"):
        errors.append("A44 should be bold")
    if a44.get("format", {}).get("horizontalAlign") != "center":
        errors.append("A44 should be center-aligned")

    # Check E44 (Q1 qty)
    e44 = cells.get("E44", {})
    e44_val = e44.get("value")
    if isinstance(e44_val, (int, float)):
        if abs(e44_val - q1_qty) > 0.01:
            errors.append(f"E44 should be {q1_qty}, got {e44_val}")
    else:
        errors.append(f"E44 should be numeric, got '{e44_val}'")

    # Check G44 (Q1 revenue, currency)
    g44 = cells.get("G44", {})
    g44_val = g44.get("value")
    if isinstance(g44_val, (int, float)):
        if abs(g44_val - q1_rev) > 0.02:
            errors.append(f"G44 should be ~{q1_rev:.2f}, got {g44_val}")
    else:
        errors.append(f"G44 should be numeric, got '{g44_val}'")
    if str(g44.get("format", {}).get("numberFormat", "")).lower() != "currency":
        errors.append("G44 should be formatted as currency")

    # Check frozen rows
    if sales.get("frozenRows", 0) < 1:
        errors.append("Header row should be frozen")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "Q1 2024 summary created correctly."
