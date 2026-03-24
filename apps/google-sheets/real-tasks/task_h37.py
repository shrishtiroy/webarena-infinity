import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    emp = None
    for s in sheets:
        if s.get("name", "") in ("Employees", "Team Directory"):
            emp = s
            break
    if emp is None and len(sheets) > 1:
        emp = sheets[1]
    if emp is None:
        return False, "Employees sheet not found."

    cells = emp.get("cells", {})

    # D27: MAX formula, green bg, currency
    d27 = cells.get("D27", {})
    formula_27 = str(d27.get("formula", "")).upper()
    if "MAX" not in formula_27:
        errors.append(f"D27 should have MAX formula, got '{d27.get('formula', '')}'")
    bg_27 = d27.get("format", {}).get("backgroundColor", "").lower()
    if bg_27 != "#c6efce":
        errors.append(f"D27 bg should be '#c6efce', got '{bg_27}'")
    if str(d27.get("format", {}).get("numberFormat", "")).lower() != "currency":
        errors.append("D27 should be formatted as currency")

    # D28: MIN formula, red bg, currency
    d28 = cells.get("D28", {})
    formula_28 = str(d28.get("formula", "")).upper()
    if "MIN" not in formula_28:
        errors.append(f"D28 should have MIN formula, got '{d28.get('formula', '')}'")
    bg_28 = d28.get("format", {}).get("backgroundColor", "").lower()
    if bg_28 != "#ffc7ce":
        errors.append(f"D28 bg should be '#ffc7ce', got '{bg_28}'")
    if str(d28.get("format", {}).get("numberFormat", "")).lower() != "currency":
        errors.append("D28 should be formatted as currency")

    # C27: "Highest Salary" bold
    c27 = cells.get("C27", {})
    if str(c27.get("value", "")).strip() != "Highest Salary":
        errors.append(f"C27 should be 'Highest Salary', got '{c27.get('value', '')}'")
    if not c27.get("format", {}).get("bold"):
        errors.append("C27 should be bold")

    # C28: "Lowest Salary" bold
    c28 = cells.get("C28", {})
    if str(c28.get("value", "")).strip() != "Lowest Salary":
        errors.append(f"C28 should be 'Lowest Salary', got '{c28.get('value', '')}'")
    if not c28.get("format", {}).get("bold"):
        errors.append("C28 should be bold")

    # Named range SalaryRange
    named_ranges = state.get("namedRanges", {})
    sr = named_ranges.get("SalaryRange")
    if sr is None:
        errors.append("Named range 'SalaryRange' not found")
    elif sr != "Employees!D2:D26":
        errors.append(f"SalaryRange should be 'Employees!D2:D26', got '{sr}'")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
