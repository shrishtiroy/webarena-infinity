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

    for r in range(2, 27):
        e_cell = cells.get(f"E{r}")
        a_cell = cells.get(f"A{r}")
        if not e_cell or not a_cell:
            continue

        date_str = str(e_cell.get("value", ""))
        name = str(a_cell.get("value", ""))
        # Parse year from MM/DD/YYYY format
        parts = date_str.split("/")
        if len(parts) != 3:
            continue
        try:
            year = int(parts[2])
        except ValueError:
            continue

        a_fmt = a_cell.get("format", {})
        bg = str(a_fmt.get("backgroundColor", "")).lower()

        if year < 2020:
            if bg != "#cfe2f3":
                errors.append(f"A{r} ({name}, started {year}) bg should be '#cfe2f3', got '{bg}'")
        elif year >= 2023:
            if bg != "#fff2cc":
                errors.append(f"A{r} ({name}, started {year}) bg should be '#fff2cc', got '{bg}'")

    # Check legend
    a28 = cells.get("A28", {})
    if str(a28.get("value", "")).strip() != "Tenure Legend":
        errors.append(f"A28 should be 'Tenure Legend', got '{a28.get('value', '')}'")
    if not a28.get("format", {}).get("bold"):
        errors.append("A28 should be bold")

    b28 = cells.get("B28", {})
    if str(b28.get("value", "")).strip() != "Blue=Pre-2020, Yellow=2023+":
        errors.append(f"B28 should be 'Blue=Pre-2020, Yellow=2023+', got '{b28.get('value', '')}'")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "Tenure-based formatting applied correctly."
