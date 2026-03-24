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

    # Check bold on products restocked in 2024
    for r in range(2, 32):
        h_cell = cells.get(f"H{r}")
        b_cell = cells.get(f"B{r}")
        if not h_cell or not b_cell:
            continue
        date_str = str(h_cell.get("value", ""))
        parts = date_str.split("/")
        if len(parts) != 3:
            continue
        try:
            year = int(parts[2])
        except ValueError:
            continue
        if year == 2024:
            if not b_cell.get("format", {}).get("bold"):
                product = b_cell.get("value", "")
                errors.append(f"B{r} ({product}, restocked {year}) should be bold")

    # Check chart
    charts = inv.get("charts", [])
    found_chart = False
    for chart in charts:
        if "Stock vs Reorder" in str(chart.get("title", "")):
            if chart.get("type") == "bar":
                found_chart = True
    if not found_chart:
        errors.append("Bar chart 'Stock vs Reorder' not found")

    # Check CF rules
    cf = inv.get("conditionalFormats", [])
    found_red = False
    found_blue = False
    for rule in cf:
        rng = rule.get("range", "")
        if "D" in rng:
            if rule.get("type") == "less_than" and str(rule.get("value", "")) == "10":
                if str(rule.get("backgroundColor", "")).lower() == "#ff0000":
                    found_red = True
            if rule.get("type") == "greater_than" and str(rule.get("value", "")) == "200":
                if str(rule.get("backgroundColor", "")).lower() == "#0000ff":
                    found_blue = True
    if not found_red:
        errors.append("Missing CF: D < 10 red bg")
    if not found_blue:
        errors.append("Missing CF: D > 200 blue bg")

    # Check freeze
    if inv.get("frozenRows", 0) < 1:
        errors.append("Header row should be frozen")
    if inv.get("frozenCols", 0) < 1:
        errors.append("First column should be frozen")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "Inventory date-based bold, chart, CF, and freeze applied correctly."
