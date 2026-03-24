import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    sa = None
    for s in sheets:
        if s.get("name", "").strip() == "Sales Analysis":
            sa = s
            break
    if sa is None:
        return False, "No sheet named 'Sales Analysis' found."

    cells = sa.get("cells", {})

    # Check frozen
    if sa.get("frozenRows", 0) < 1:
        errors.append("Header row should be frozen on 'Sales Analysis'")

    # Check sorted by Total (G) descending
    prev_total = None
    for r in range(2, 42):
        g_cell = cells.get(f"G{r}")
        if g_cell and isinstance(g_cell.get("value"), (int, float)):
            val = g_cell["value"]
            if prev_total is not None and val > prev_total:
                errors.append(
                    f"Not sorted desc by Total: G{r} ({val}) > G{r-1} ({prev_total})"
                )
                break
            prev_total = val

    # Check bar chart exists with correct title
    charts = sa.get("charts", [])
    found_chart = False
    for chart in charts:
        if (chart.get("type") == "bar"
                and chart.get("title", "").strip() == "Top Sales by Amount"):
            found_chart = True
            break
    if not found_chart:
        errors.append("No bar chart titled 'Top Sales by Amount' found on 'Sales Analysis'")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
