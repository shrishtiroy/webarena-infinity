import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][2]
    cell = sheet["cells"].get("B30")
    if not cell:
        return False, "Cell B30 not found in Inventory sheet."
    fmt = cell.get("format", {})
    if fmt.get("strikethrough") == True:
        return True, "Cell B30 has strikethrough."
    return False, f"Cell B30 does not have strikethrough. Format: {fmt}"
