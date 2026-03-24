import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][1]
    cell = sheet["cells"].get("D29")
    if not cell:
        return False, "Cell D29 not found in Employees sheet."
    formula = cell.get("formula", "")
    if formula != "=MIN(D2:D26)":
        return False, f"Cell D29 formula is '{formula}', expected '=MIN(D2:D26)'."
    value = cell.get("value")
    if not isinstance(value, (int, float)):
        return False, f"Cell D29 value is '{value}', expected a number."
    return True, f"Cell D29 has formula '=MIN(D2:D26)' and numeric value {value}."
