import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    cell = sheet["cells"].get("A1")
    if not cell:
        return False, "Cell A1 not found in Sales sheet."
    fmt = cell.get("format", {})
    font_color = fmt.get("fontColor", "")
    if font_color == "#ff0000":
        return True, "Cell A1 has fontColor '#ff0000'."
    return False, f"Cell A1 fontColor is '{font_color}', expected '#ff0000'. Format: {fmt}"
