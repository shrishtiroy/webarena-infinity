import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][1]
    cell = sheet["cells"].get("B3")
    if not cell:
        return False, "Cell B3 not found in Employees sheet."
    fmt = cell.get("format", {})
    if fmt.get("italic") == True:
        return True, "Cell B3 is italic."
    return False, f"Cell B3 is not italic. Format: {fmt}"
