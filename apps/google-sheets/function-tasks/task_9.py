import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    cell = sheet["cells"].get("A2")
    if not cell:
        return False, "Cell A2 not found in Sales sheet."
    fmt = cell.get("format", {})
    if fmt.get("bold") == True:
        return True, "Cell A2 is bold."
    return False, f"Cell A2 is not bold. Format: {fmt}"
