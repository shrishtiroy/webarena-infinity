import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][1]
    cell = sheet["cells"].get("D2")
    if cell and cell.get("value") == 62000:
        return True, "Employees sorted by Salary ascending. First row has min salary 62000."
    return False, f"Expected D2 value 62000, got {cell.get('value') if cell else 'no cell'}."
