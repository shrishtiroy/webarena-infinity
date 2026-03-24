import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][2]
    if sheet.get("frozenRows") == 3:
        return True, "First 3 rows frozen on Inventory sheet."
    return False, f"frozenRows is {sheet.get('frozenRows')}, expected 3."
