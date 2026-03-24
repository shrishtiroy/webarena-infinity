import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    es = None
    for s in sheets:
        if s.get("name", "").strip() == "Executive Summary":
            es = s
            break
    if es is None:
        return False, "No sheet named 'Executive Summary' found."

    cells = es.get("cells", {})

    # Check A1 title and merge
    a1 = cells.get("A1", {})
    if str(a1.get("value", "")).strip() != "Company Dashboard":
        errors.append(
            f"A1 should be 'Company Dashboard', got '{a1.get('value', '')}'"
        )
    if not a1.get("format", {}).get("bold"):
        errors.append("A1 should be bold")

    merged = es.get("mergedCells", [])
    if "A1:B1" not in merged:
        errors.append("A1:B1 should be merged")

    # Check rows 3-6
    expected_rows = [
        ("A3", "Total Revenue", "B3", "SUM", True),
        ("A4", "Total Payroll", "B4", "SUM", True),
        ("A5", "Average Salary", "B5", "AVERAGE", True),
        ("A6", "Inventory Items", "B6", "COUNTA", False),
    ]

    for label_addr, label_text, formula_addr, formula_fn, needs_currency in expected_rows:
        # Label
        label_cell = cells.get(label_addr, {})
        if str(label_cell.get("value", "")).strip() != label_text:
            errors.append(
                f"{label_addr} should be '{label_text}', got '{label_cell.get('value', '')}'"
            )
        if not label_cell.get("format", {}).get("bold"):
            errors.append(f"{label_addr} should be bold")

        # Formula
        f_cell = cells.get(formula_addr, {})
        formula = str(f_cell.get("formula", "")).upper()
        if formula_fn not in formula:
            errors.append(
                f"{formula_addr} should have {formula_fn} formula, "
                f"got '{f_cell.get('formula', '')}'"
            )

        if needs_currency:
            fmt = f_cell.get("format", {})
            if str(fmt.get("numberFormat", "")).lower() != "currency":
                errors.append(f"{formula_addr} should be formatted as currency")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
