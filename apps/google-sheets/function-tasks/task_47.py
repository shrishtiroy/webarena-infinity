import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][1]
    if sheet.get("frozenCols") == 2:
        return True, "First 2 columns frozen on Employees sheet."
    return False, f"frozenCols is {sheet.get('frozenCols')}, expected 2."
