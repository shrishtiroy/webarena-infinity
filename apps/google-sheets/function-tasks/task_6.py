import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    cell = sheet["cells"].get("H2")
    if not cell:
        return True, "Cell H2 does not exist in Sales sheet (cleared)."
    value = cell.get("value")
    if value is None or value == "" or value == 0:
        return True, f"Cell H2 has null/empty value (cleared). Value: {repr(value)}."
    return False, f"Cell H2 still has value '{value}', expected it to be cleared."
