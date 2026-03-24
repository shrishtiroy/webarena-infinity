import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Sales sheet is at index 0
    sheets = state.get("sheets", [])
    sales_sheet = None
    for s in sheets:
        if s.get("name", "").lower() in ("sales", "revenue data", "main data"):
            sales_sheet = s
            break
    if sales_sheet is None and len(sheets) > 0:
        sales_sheet = sheets[0]
    if sales_sheet is None:
        return False, "Sales sheet not found."

    cells = sales_sheet.get("cells", {})

    # A45: "Count", bold
    a45 = cells.get("A45", {})
    if str(a45.get("value", "")).strip() != "Count":
        errors.append(f"A45 value should be 'Count', got '{a45.get('value', '')}'")
    fmt_a45 = a45.get("format", {})
    if not fmt_a45.get("bold"):
        errors.append("A45 should be bold")

    # E45: formula with COUNT
    e45 = cells.get("E45", {})
    formula_e45 = str(e45.get("formula", "")).upper()
    if "COUNT" not in formula_e45:
        errors.append(f"E45 should have a COUNT formula, got '{e45.get('formula', '')}'")

    # A46: "Avg Price", bold
    a46 = cells.get("A46", {})
    if str(a46.get("value", "")).strip() != "Avg Price":
        errors.append(f"A46 value should be 'Avg Price', got '{a46.get('value', '')}'")
    fmt_a46 = a46.get("format", {})
    if not fmt_a46.get("bold"):
        errors.append("A46 should be bold")

    # F46: formula with AVERAGE
    f46 = cells.get("F46", {})
    formula_f46 = str(f46.get("formula", "")).upper()
    if "AVERAGE" not in formula_f46:
        errors.append(f"F46 should have an AVERAGE formula, got '{f46.get('formula', '')}'")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
