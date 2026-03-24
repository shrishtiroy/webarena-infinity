import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][1]
    cell = sheet["cells"].get("H1")
    if not cell:
        return False, "Cell H1 not found in Employees sheet."
    if cell.get("value") == "Notes":
        return True, "Cell H1 has value 'Notes'."
    return False, f"Cell H1 value is '{cell.get('value')}', expected 'Notes'."
