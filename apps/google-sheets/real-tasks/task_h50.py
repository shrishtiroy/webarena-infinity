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

    # Check sorted by G desc
    cells = sales.get("cells", {})
    prev_val = None
    for r in range(2, 42):
        g_cell = cells.get(f"G{r}")
        if g_cell and isinstance(g_cell.get("value"), (int, float)):
            val = g_cell["value"]
            if prev_val is not None and val > prev_val + 0.01:
                errors.append(f"G{r} ({val}) > G{r-1} ({prev_val}): not sorted desc")
                break
            prev_val = val

    # Check frozen rows
    if sales.get("frozenRows", 0) < 1:
        errors.append("Header row should be frozen")

    # Check filter mode
    if not sales.get("filterMode"):
        errors.append("Filter mode should be enabled")

    # Check East is hidden
    filters = sales.get("filters", {})
    d_filter = filters.get("D", {})
    hidden = d_filter.get("hiddenValues", [])
    if "East" not in hidden:
        errors.append("East region should be hidden in filters")

    # Check CF rules
    cf = sales.get("conditionalFormats", [])
    found_green = False
    found_red = False
    for rule in cf:
        rng = rule.get("range", "")
        if "G" in rng:
            if rule.get("type") == "greater_than" and str(rule.get("value", "")) == "8000":
                if str(rule.get("backgroundColor", "")).lower() == "#c6efce":
                    found_green = True
            if rule.get("type") == "less_than" and str(rule.get("value", "")) == "500":
                if str(rule.get("backgroundColor", "")).lower() == "#ffc7ce":
                    found_red = True
    if not found_green:
        errors.append("Missing CF rule: G > 8000 green")
    if not found_red:
        errors.append("Missing CF rule: G < 500 red")

    # Check chart
    charts = sales.get("charts", [])
    found_chart = False
    for chart in charts:
        if "Revenue Distribution" in str(chart.get("title", "")):
            if chart.get("type") == "bar":
                found_chart = True
    if not found_chart:
        errors.append("Bar chart 'Revenue Distribution' not found")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "Sales sorted, filtered, with CF and chart."
