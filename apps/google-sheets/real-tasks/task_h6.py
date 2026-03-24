import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    errors = []

    # Find Dashboard sheet
    sheets = state.get("sheets", [])
    dashboard = None
    for s in sheets:
        if s.get("name", "").strip() == "Dashboard":
            dashboard = s
            break

    if dashboard is None:
        return False, "No sheet named 'Dashboard' found."

    cells = dashboard.get("cells", {})

    # A1: "Total Revenue", bold
    a1 = cells.get("A1", {})
    if str(a1.get("value", "")).strip() != "Total Revenue":
        errors.append(f"A1 value should be 'Total Revenue', got '{a1.get('value', '')}'")
    fmt_a1 = a1.get("format", {})
    if not fmt_a1.get("bold"):
        errors.append("A1 should be bold")

    # B1: formula with SUM
    b1 = cells.get("B1", {})
    formula_b1 = str(b1.get("formula", "")).upper()
    if "SUM" not in formula_b1:
        errors.append(f"B1 should have a SUM formula, got '{b1.get('formula', '')}'")

    # A2: "Employee Count", bold
    a2 = cells.get("A2", {})
    if str(a2.get("value", "")).strip() != "Employee Count":
        errors.append(f"A2 value should be 'Employee Count', got '{a2.get('value', '')}'")
    fmt_a2 = a2.get("format", {})
    if not fmt_a2.get("bold"):
        errors.append("A2 should be bold")

    # B2: formula with COUNTA
    b2 = cells.get("B2", {})
    formula_b2 = str(b2.get("formula", "")).upper()
    if "COUNTA" not in formula_b2:
        errors.append(f"B2 should have a COUNTA formula, got '{b2.get('formula', '')}'")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
