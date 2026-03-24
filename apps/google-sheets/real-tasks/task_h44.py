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

    # Compute department averages
    dept_salaries = defaultdict(list)
    for r in range(2, 27):
        dept_cell = cells.get(f"B{r}")
        sal_cell = cells.get(f"D{r}")
        if dept_cell and sal_cell and isinstance(sal_cell.get("value"), (int, float)):
            dept = str(dept_cell.get("value", ""))
            dept_salaries[dept].append((r, sal_cell["value"]))

    dept_avgs = {d: sum(s for _, s in rows) / len(rows) for d, rows in dept_salaries.items()}

    above_count = 0
    below_count = 0
    for dept, rows in dept_salaries.items():
        avg = dept_avgs[dept]
        for r, sal in rows:
            d_cell = cells.get(f"D{r}", {})
            font_color = str(d_cell.get("format", {}).get("fontColor", "")).lower()
            if sal > avg:
                above_count += 1
                if font_color != "#006100":
                    errors.append(f"D{r} above avg: expected green text (#006100), got '{font_color}'")
            elif sal < avg:
                below_count += 1
                if font_color != "#ff0000":
                    errors.append(f"D{r} below avg: expected red text (#ff0000), got '{font_color}'")

    # Check summary labels
    a27 = cells.get("A27", {})
    if str(a27.get("value", "")).strip() != "Above Avg":
        errors.append(f"A27 should be 'Above Avg', got '{a27.get('value', '')}'")
    if not a27.get("format", {}).get("bold"):
        errors.append("A27 should be bold")

    b27 = cells.get("B27", {})
    b27_val = b27.get("value")
    if isinstance(b27_val, (int, float)):
        b27_val = int(b27_val)
    if b27_val != above_count:
        errors.append(f"B27 should be {above_count}, got '{b27_val}'")

    a28 = cells.get("A28", {})
    if str(a28.get("value", "")).strip() != "Below Avg":
        errors.append(f"A28 should be 'Below Avg', got '{a28.get('value', '')}'")
    if not a28.get("format", {}).get("bold"):
        errors.append("A28 should be bold")

    b28 = cells.get("B28", {})
    b28_val = b28.get("value")
    if isinstance(b28_val, (int, float)):
        b28_val = int(b28_val)
    if b28_val != below_count:
        errors.append(f"B28 should be {below_count}, got '{b28_val}'")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "Salary vs department average formatting applied correctly."
