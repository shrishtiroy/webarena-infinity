import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][1]
    cell = sheet["cells"].get("G2")
    if not cell:
        return False, "Cell G2 not found in Employees sheet."
    fmt = cell.get("format", {})
    bg_color = fmt.get("backgroundColor", "")
    if bg_color == "#90ee90":
        return True, "Cell G2 has backgroundColor '#90ee90'."
    return False, f"Cell G2 backgroundColor is '{bg_color}', expected '#90ee90'. Format: {fmt}"
