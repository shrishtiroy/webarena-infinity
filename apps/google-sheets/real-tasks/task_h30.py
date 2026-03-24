import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    kpi = None
    for s in sheets:
        if s.get("name", "").strip() == "KPI Dashboard":
            kpi = s
            break
    if kpi is None:
        return False, "No sheet named 'KPI Dashboard' found."

    cells = kpi.get("cells", {})

    expected = [
        ("A1", "Total Revenue", "B1", "SUM", True),
        ("A2", "Average Sale", "B2", "AVERAGE", True),
        ("A3", "Max Sale", "B3", "MAX", True),
        ("A4", "Headcount", "B4", "COUNTA", False),
        ("A5", "Avg Salary", "B5", "AVERAGE", True),
    ]

    for label_cell, label_text, formula_cell, formula_fn, needs_currency in expected:
        # Check label
        a = cells.get(label_cell, {})
        if str(a.get("value", "")).strip() != label_text:
            errors.append(
                f"{label_cell} should be '{label_text}', got '{a.get('value', '')}'"
            )
        if not a.get("format", {}).get("bold"):
            errors.append(f"{label_cell} should be bold")

        # Check formula
        b = cells.get(formula_cell, {})
        formula = str(b.get("formula", "")).upper()
        if formula_fn not in formula:
            errors.append(
                f"{formula_cell} should have {formula_fn} formula, "
                f"got '{b.get('formula', '')}'"
            )

        # Check currency format
        if needs_currency:
            fmt = b.get("format", {})
            if str(fmt.get("numberFormat", "")).lower() != "currency":
                errors.append(f"{formula_cell} should be formatted as currency")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
