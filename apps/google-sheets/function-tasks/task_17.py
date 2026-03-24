import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][1]
    cell = sheet["cells"].get("D2")
    if not cell:
        return False, "Cell D2 not found in Employees sheet."
    fmt = cell.get("format", {})
    num_fmt = fmt.get("numberFormat", "")
    if num_fmt == "percentage":
        return True, "Cell D2 has numberFormat 'percentage'."
    return False, f"Cell D2 numberFormat is '{num_fmt}', expected 'percentage'. Format: {fmt}"
