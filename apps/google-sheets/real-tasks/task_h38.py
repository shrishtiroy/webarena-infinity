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
        if s.get("name", "") in ("Sales", "Revenue", "Revenue Data"):
            sales = s
            break
    if sales is None:
        sales = sheets[0]

    cells = sales.get("cells", {})

    # Check filter mode
    if not sales.get("filterMode"):
        errors.append("Filter mode should be enabled on Sales")

    # Check filter hides West
    filters = sales.get("filters", {})
    d_filter = filters.get("D")
    if d_filter is None:
        errors.append("No filter set on column D (Region)")
    else:
        hidden = d_filter.get("hiddenValues", [])
        if "West" not in hidden:
            errors.append(f"Filter should hide 'West', hiddenValues: {hidden}")

    # Check no "Wireless Mouse" in B column (should be "Wireless Mouse Pro")
    found_old = False
    found_new = False
    for r in range(2, 42):
        b_cell = cells.get(f"B{r}")
        if b_cell:
            val = str(b_cell.get("value", ""))
            if val == "Wireless Mouse":
                found_old = True
            if val == "Wireless Mouse Pro":
                found_new = True

    if found_old:
        errors.append("'Wireless Mouse' still found (should be 'Wireless Mouse Pro')")
    if not found_new:
        errors.append("'Wireless Mouse Pro' not found")

    # Check B1 text color
    b1 = cells.get("B1", {})
    fc = b1.get("format", {}).get("fontColor", "").lower()
    if fc != "#0000ff":
        errors.append(f"B1 fontColor should be '#0000ff', got '{fc}'")

    # Check named range
    named_ranges = state.get("namedRanges", {})
    sr = named_ranges.get("SalesRegion")
    if sr is None:
        errors.append("Named range 'SalesRegion' not found")
    elif sr != "Sales!D2:D41":
        errors.append(f"SalesRegion should be 'Sales!D2:D41', got '{sr}'")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
