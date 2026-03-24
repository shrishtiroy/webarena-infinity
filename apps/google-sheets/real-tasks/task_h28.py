import requests
from collections import defaultdict


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

    # Calculate department totals from state
    dept_totals = defaultdict(float)
    dept_rows = defaultdict(list)
    for r in range(2, 27):
        dept_cell = cells.get(f"B{r}")
        sal_cell = cells.get(f"D{r}")
        if dept_cell and sal_cell:
            dept = str(dept_cell.get("value", ""))
            sal = sal_cell.get("value", 0)
            if isinstance(sal, (int, float)):
                dept_totals[dept] += sal
                dept_rows[dept].append(r)

    if not dept_totals:
        return False, "No department/salary data found."

    top_dept = max(dept_totals, key=dept_totals.get)

    # Check salary cells for top dept have green bg
    for r in dept_rows[top_dept]:
        d_cell = cells.get(f"D{r}", {})
        bg = d_cell.get("format", {}).get("backgroundColor", "").lower()
        if bg != "#c6efce":
            errors.append(
                f"D{r} (dept '{top_dept}') bg should be '#c6efce', got '{bg}'"
            )

    # Check A27 label
    a27 = cells.get("A27", {})
    a27_val = str(a27.get("value", "")).strip()
    if a27_val != "Highest Dept":
        errors.append(f"A27 should be 'Highest Dept', got '{a27_val}'")
    if not a27.get("format", {}).get("bold"):
        errors.append("A27 should be bold")

    # Check B27 has department name
    b27 = cells.get("B27", {})
    b27_val = str(b27.get("value", "")).strip()
    if b27_val != top_dept:
        errors.append(f"B27 should be '{top_dept}', got '{b27_val}'")

    if errors:
        return False, "; ".join(errors)
    return True, "All checks passed."
