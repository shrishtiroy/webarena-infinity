import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    cell = sheet["cells"].get("E2")
    if not cell:
        return False, "Cell E2 not found in Sales sheet."
    fmt = cell.get("format", {})
    num_fmt = fmt.get("numberFormat", "")
    if num_fmt == "number":
        return True, "Cell E2 has numberFormat 'number'."
    return False, f"Cell E2 numberFormat is '{num_fmt}', expected 'number'. Format: {fmt}"
