import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][2]
    cell = sheet["cells"].get("C2")
    if not cell:
        return False, "Cell C2 not found in Inventory sheet."
    fmt = cell.get("format", {})
    if fmt.get("underline") == True:
        return True, "Cell C2 is underlined."
    return False, f"Cell C2 is not underlined. Format: {fmt}"
