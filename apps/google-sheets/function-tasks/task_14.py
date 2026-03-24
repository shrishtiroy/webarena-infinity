import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][1]
    cell = sheet["cells"].get("G6")
    if not cell:
        return False, "Cell G6 not found in Employees sheet."
    fmt = cell.get("format", {})
    bg_color = fmt.get("backgroundColor", "")
    if bg_color == "#ffff00":
        return True, "Cell G6 has backgroundColor '#ffff00'."
    return False, f"Cell G6 backgroundColor is '{bg_color}', expected '#ffff00'. Format: {fmt}"
