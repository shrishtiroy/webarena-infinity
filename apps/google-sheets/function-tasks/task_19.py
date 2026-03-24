import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][2]
    cell = sheet["cells"].get("A1")
    if not cell:
        return False, "Cell A1 not found in Inventory sheet."
    fmt = cell.get("format", {})
    align = fmt.get("horizontalAlign", "")
    if align == "center":
        return True, "Cell A1 has horizontalAlign 'center'."
    return False, f"Cell A1 horizontalAlign is '{align}', expected 'center'. Format: {fmt}"
