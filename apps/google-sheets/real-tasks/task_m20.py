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
    bg_color = fmt.get("backgroundColor", "")
    errors = []
    if font_color != "#ff0000":
        errors.append(f"fontColor is '{font_color}', expected '#ff0000'")
    if bg_color != "#e0e0e0":
        errors.append(f"backgroundColor is '{bg_color}', expected '#e0e0e0'")
    if errors:
        return False, "; ".join(errors) + f". Full format: {fmt}"
    return True, "Cell A1 (Date header) has red text (#ff0000) and light gray background (#e0e0e0)."
