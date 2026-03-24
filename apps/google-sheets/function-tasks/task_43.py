import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    cell = sheet["cells"].get("E2")
    if cell and cell.get("value") == 50:
        return True, "Sales sorted by Quantity descending. First row has max qty 50."
    return False, f"Expected E2 value 50, got {cell.get('value') if cell else 'no cell'}."
