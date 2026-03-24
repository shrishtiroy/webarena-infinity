import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][1]
    cell = sheet["cells"].get("G2")
    if not cell:
        return False, "Cell G2 not found."
    v = cell.get("validation")
    if not v:
        return False, "No validation set on G2."
    if v.get("type") == "list" and "Active" in v.get("values", "") and "Terminated" in v.get("values", ""):
        return True, "Data validation set on G2."
    return False, f"Validation: {v}"
