import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][1]
    cell = sheet["cells"].get("D28")
    if not cell:
        return False, "Cell D28 not found in Employees sheet."
    formula = cell.get("formula", "")
    if not formula or "AVERAGE" not in formula.upper():
        return False, f"Cell D28 formula is '{formula}', expected a formula containing 'AVERAGE'."
    fmt = cell.get("format", {})
    number_format = fmt.get("numberFormat", "")
    if number_format != "currency":
        return False, f"Cell D28 numberFormat is '{number_format}', expected 'currency'. Format: {fmt}"
    return True, f"Cell D28 has AVERAGE formula ('{formula}') and currency format."
