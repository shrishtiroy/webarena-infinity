import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Employees sheet is at index 1
    sheets = state.get("sheets", [])
    emp_sheet = None
    for s in sheets:
        if s.get("name", "").lower() in ("employees", "team directory"):
            emp_sheet = s
            break
    if emp_sheet is None and len(sheets) > 1:
        emp_sheet = sheets[1]
    if emp_sheet is None:
        return False, "Employees sheet not found."

    cells = emp_sheet.get("cells", {})

    # --- A27: "Total", bold ---
    a27 = cells.get("A27", {})
    if str(a27.get("value", "")).strip().lower() != "total":
        errors.append(f"A27 value should be 'Total', got '{a27.get('value', '')}'")
    fmt_a27 = a27.get("format", {})
    if not fmt_a27.get("bold"):
        errors.append("A27 should be bold")

    # --- D27: SUM formula, currency ---
    d27 = cells.get("D27", {})
    formula_d27 = str(d27.get("formula", "")).upper()
    if "SUM" not in formula_d27:
        errors.append(f"D27 should have a SUM formula, got '{d27.get('formula', '')}'")
    fmt_d27 = d27.get("format", {})
    if str(fmt_d27.get("numberFormat", "")).lower() != "currency":
        errors.append(f"D27 numberFormat should be 'currency', got '{fmt_d27.get('numberFormat', '')}'")

    # --- A28: "Average", bold ---
    a28 = cells.get("A28", {})
    if str(a28.get("value", "")).strip().lower() != "average":
        errors.append(f"A28 value should be 'Average', got '{a28.get('value', '')}'")
    fmt_a28 = a28.get("format", {})
    if not fmt_a28.get("bold"):
        errors.append("A28 should be bold")

    # --- D28: AVERAGE formula, currency ---
    d28 = cells.get("D28", {})
    formula_d28 = str(d28.get("formula", "")).upper()
    if "AVERAGE" not in formula_d28:
        errors.append(f"D28 should have an AVERAGE formula, got '{d28.get('formula', '')}'")
    fmt_d28 = d28.get("format", {})
    if str(fmt_d28.get("numberFormat", "")).lower() != "currency":
        errors.append(f"D28 numberFormat should be 'currency', got '{fmt_d28.get('numberFormat', '')}'")

    # --- A29: "Minimum", bold ---
    a29 = cells.get("A29", {})
    if str(a29.get("value", "")).strip().lower() != "minimum":
        errors.append(f"A29 value should be 'Minimum', got '{a29.get('value', '')}'")
    fmt_a29 = a29.get("format", {})
    if not fmt_a29.get("bold"):
        errors.append("A29 should be bold")

    # --- D29: MIN formula, currency ---
    d29 = cells.get("D29", {})
    formula_d29 = str(d29.get("formula", "")).upper()
    if "MIN" not in formula_d29:
        errors.append(f"D29 should have a MIN formula, got '{d29.get('formula', '')}'")
    fmt_d29 = d29.get("format", {})
    if str(fmt_d29.get("numberFormat", "")).lower() != "currency":
        errors.append(f"D29 numberFormat should be 'currency', got '{fmt_d29.get('numberFormat', '')}'")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
