import requests
from collections import Counter


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
    dept_counter = Counter()
    dept_employees = {}
    for r in range(2, 27):
        dept_cell = cells.get(f"B{r}")
        if dept_cell and dept_cell.get("value"):
            dept = str(dept_cell["value"])
            dept_counter[dept] += 1
            if dept not in dept_employees:
                dept_employees[dept] = []
            name = cells.get(f"A{r}", {}).get("value", "")
            title = cells.get(f"C{r}", {}).get("value", "")
            salary = cells.get(f"D{r}", {}).get("value", 0)
            dept_employees[dept].append((name, title, salary))

    if not dept_counter:
        return False, "No department data found."

    smallest_dept = min(dept_counter, key=dept_counter.get)
    emps = dept_employees[smallest_dept]

    # Find the new sheet
    dept_sheet = None
    for s in sheets:
        if s.get("name", "").strip() == smallest_dept:
            dept_sheet = s
            break
    if dept_sheet is None:
        return False, f"No sheet named '{smallest_dept}' found. Current sheets: {[s['name'] for s in sheets]}"

    ds_cells = dept_sheet.get("cells", {})

    # Check headers
    for col, header in [("A", "Name"), ("B", "Title"), ("C", "Salary")]:
        cell = ds_cells.get(f"{col}1", {})
        if str(cell.get("value", "")).strip() != header:
            errors.append(f"{col}1 should be '{header}', got '{cell.get('value', '')}'")
        if not cell.get("format", {}).get("bold"):
            errors.append(f"{col}1 should be bold")

    # Check employees are listed
    highest_sal = max(emps, key=lambda x: x[2])
    for i, (name, title, salary) in enumerate(emps):
        row = i + 2
        a_val = str(ds_cells.get(f"A{row}", {}).get("value", "")).strip()
        if a_val != name:
            errors.append(f"A{row} should be '{name}', got '{a_val}'")

    # Check highest-paid name is bold
    for row in range(2, 2 + len(emps)):
        a_cell = ds_cells.get(f"A{row}", {})
        if str(a_cell.get("value", "")).strip() == highest_sal[0]:
            if not a_cell.get("format", {}).get("bold"):
                errors.append(f"A{row} ({highest_sal[0]}) should be bold (highest paid)")
            break

    if errors:
        return False, "; ".join(errors[:5])
    return True, f"Department '{smallest_dept}' sheet created correctly."
