import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    cell = sheet["cells"].get("D42")
    if not cell:
        return False, "Cell D42 not found in Sales sheet."
    fmt = cell.get("format", {})
    align = fmt.get("horizontalAlign", "")
    if align == "right":
        return True, "Cell D42 has horizontalAlign 'right'."
    return False, f"Cell D42 horizontalAlign is '{align}', expected 'right'. Format: {fmt}"
