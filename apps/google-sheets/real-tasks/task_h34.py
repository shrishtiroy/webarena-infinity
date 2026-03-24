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

    # Find TechDist Global rows and check supplier cell bg
    techd_rows = []
    for r in range(2, 32):
        g_cell = cells.get(f"G{r}")
        if g_cell and str(g_cell.get("value", "")).strip() == "TechDist Global":
            techd_rows.append(r)
            bg = g_cell.get("format", {}).get("backgroundColor", "").lower()
            if bg != "#e0e0e0":
                errors.append(f"G{r} (TechDist Global) bg should be '#e0e0e0', got '{bg}'")

    if not techd_rows:
        errors.append("No 'TechDist Global' supplier cells found")

    # Check bar chart
    charts = inv.get("charts", [])
    found_chart = False
    for chart in charts:
        if chart.get("type") == "bar" and chart.get("title", "").strip() == "Stock Levels":
            found_chart = True
            break
    if not found_chart:
        errors.append("No bar chart titled 'Stock Levels' found on Inventory")

    # Check frozen
    if inv.get("frozenRows", 0) < 1:
        errors.append("Header row should be frozen")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
