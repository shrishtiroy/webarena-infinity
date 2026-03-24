import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][1]
    cell = sheet["cells"].get("D27")
    if not cell:
        return False, "Cell D27 not found in Employees sheet."
    formula = cell.get("formula", "")
    if formula != "=SUM(D2:D26)":
        return False, f"Cell D27 formula is '{formula}', expected '=SUM(D2:D26)'."
    value = cell.get("value")
    if not isinstance(value, (int, float)):
        return False, f"Cell D27 value is '{value}', expected a number (sum of salaries)."
    return True, f"Cell D27 has formula '=SUM(D2:D26)' and numeric value {value}."
