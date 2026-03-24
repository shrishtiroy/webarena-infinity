import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    if sheet.get("frozenRows") == 1:
        return True, "First row frozen on Sales sheet."
    return False, f"frozenRows is {sheet.get('frozenRows')}, expected 1."
