import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    cell = sheet["cells"].get("F2")
    if not cell:
        return False, "Cell F2 not found in Sales sheet."
    fmt = cell.get("format", {})
    decimal_places = fmt.get("decimalPlaces")
    if decimal_places == 0:
        return True, "Cell F2 has decimalPlaces 0."
    return False, f"Cell F2 decimalPlaces is '{decimal_places}', expected 0. Format: {fmt}"
