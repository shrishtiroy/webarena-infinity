import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the Sales sheet (index 0)
    if len(state["sheets"]) < 1:
        return False, "Sales sheet not found (no sheets)."
    sheet = state["sheets"][0]

    cell = sheet["cells"].get("D42")
    if cell is None:
        return False, "Cell D42 not found on the Sales sheet."

    fmt = cell.get("format", {})
    h_align = fmt.get("horizontalAlign")
    if h_align == "right":
        return True, "Cell D42 on the Sales sheet is right-aligned."
    return False, f"Expected D42 horizontalAlign to be 'right', but found '{h_align}'."
