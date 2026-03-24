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

    # Check I1 header
    i1 = cells.get("I1", {})
    if str(i1.get("value", "")).strip() != "Commission":
        errors.append(f"I1 should be 'Commission', got '{i1.get('value', '')}'")
    if not i1.get("format", {}).get("bold"):
        errors.append("I1 should be bold")

    # Check sample formula cells (I2, I10, I41)
    for r in [2, 10, 41]:
        i_cell = cells.get(f"I{r}", {})
        formula = str(i_cell.get("formula", "")).upper()
        if f"G{r}" not in formula or "0.05" not in str(i_cell.get("formula", "")):
            errors.append(
                f"I{r} should have a formula referencing G{r} and 0.05, "
                f"got '{i_cell.get('formula', '')}'"
            )
        fmt = i_cell.get("format", {})
        if str(fmt.get("numberFormat", "")).lower() != "currency":
            errors.append(f"I{r} should be formatted as currency")

    # Check I42 SUM formula and bold
    i42 = cells.get("I42", {})
    formula_42 = str(i42.get("formula", "")).upper()
    if "SUM" not in formula_42:
        errors.append(f"I42 should have a SUM formula, got '{i42.get('formula', '')}'")
    if not i42.get("format", {}).get("bold"):
        errors.append("I42 should be bold")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
