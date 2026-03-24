import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][2]
    cell = sheet["cells"].get("D2")
    if cell and cell.get("value") == 0:
        return True, "Inventory sorted by Stock ascending. First row has stock 0."
    return False, f"Expected D2 value 0, got {cell.get('value') if cell else 'no cell'}."
