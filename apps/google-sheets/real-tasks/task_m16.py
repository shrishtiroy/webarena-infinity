import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    frozen = sheet.get("frozenRows")
    filter_mode = sheet.get("filterMode")
    errors = []
    if frozen != 1:
        errors.append(f"frozenRows is {frozen}, expected 1")
    if filter_mode != True:
        errors.append(f"filterMode is {filter_mode}, expected True")
    if errors:
        return False, "; ".join(errors) + "."
    return True, "Header row frozen (frozenRows=1) and filter mode enabled on Sales sheet."
