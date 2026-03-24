import requests
from collections import Counter, defaultdict


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

    # Count employees per department
    dept_counter = Counter()
    dept_rows = defaultdict(list)
    for r in range(2, 27):
        dept_cell = cells.get(f"B{r}")
        if dept_cell and dept_cell.get("value"):
            dept = str(dept_cell["value"])
            dept_counter[dept] += 1
            dept_rows[dept].append(r)

    if not dept_counter:
        return False, "No department data found."

    largest_dept = max(dept_counter, key=dept_counter.get)
    largest_count = dept_counter[largest_dept]

    # Check A27, B27, C27
    a27 = cells.get("A27", {})
    if str(a27.get("value", "")).strip() != "Largest Dept":
        errors.append(f"A27 should be 'Largest Dept', got '{a27.get('value', '')}'")
    if not a27.get("format", {}).get("bold"):
        errors.append("A27 should be bold")

    b27 = cells.get("B27", {})
    if str(b27.get("value", "")).strip() != largest_dept:
        errors.append(f"B27 should be '{largest_dept}', got '{b27.get('value', '')}'")

    c27 = cells.get("C27", {})
    c27_val = c27.get("value")
    if isinstance(c27_val, (int, float)):
        c27_val = int(c27_val)
    if c27_val != largest_count:
        errors.append(f"C27 should be {largest_count}, got '{c27_val}'")

    # Check name cells for largest dept have green bg
    for r in dept_rows[largest_dept]:
        a_cell = cells.get(f"A{r}", {})
        bg = str(a_cell.get("format", {}).get("backgroundColor", "")).lower()
        if bg != "#c6efce":
            errors.append(f"A{r} (dept '{largest_dept}') bg should be '#c6efce', got '{bg}'")

    # Check CF: salary > 100000 green
    cf = emp.get("conditionalFormats", [])
    found_cf = False
    for rule in cf:
        rng = rule.get("range", "")
        if "D" in rng:
            if rule.get("type") == "greater_than" and str(rule.get("value", "")) == "100000":
                if str(rule.get("backgroundColor", "")).lower() == "#c6efce":
                    found_cf = True
    if not found_cf:
        errors.append("Missing CF: D > 100000 with green bg")

    if errors:
        return False, "; ".join(errors[:5])
    return True, f"Largest department '{largest_dept}' identified and formatted correctly."
