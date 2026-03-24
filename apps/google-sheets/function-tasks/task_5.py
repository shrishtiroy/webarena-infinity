import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    cell = sheet["cells"].get("E43")
    if not cell:
        return False, "Cell E43 not found in Sales sheet."
    formula = cell.get("formula", "")
    if formula != "=MAX(E2:E41)":
        return False, f"Cell E43 formula is '{formula}', expected '=MAX(E2:E41)'."
    value = cell.get("value")
    if not isinstance(value, (int, float)):
        return False, f"Cell E43 value is '{value}', expected a number."
    return True, f"Cell E43 has formula '=MAX(E2:E41)' and numeric value {value}."
