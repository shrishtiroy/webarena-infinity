import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    cell = sheet["cells"].get("A43")
    if not cell:
        return False, "Cell A43 not found in Sales sheet."
    if cell.get("value") == "Grand Total":
        return True, "Cell A43 has value 'Grand Total'."
    return False, f"Cell A43 value is '{cell.get('value')}', expected 'Grand Total'."
