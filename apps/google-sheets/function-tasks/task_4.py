import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][2]
    cell = sheet["cells"].get("D30")
    if not cell:
        return False, "Cell D30 not found in Inventory sheet."
    value = cell.get("value")
    if value == 500 or value == "500":
        return True, f"Cell D30 has value {value}."
    return False, f"Cell D30 value is '{value}', expected 500."
