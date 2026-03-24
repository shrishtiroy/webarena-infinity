import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    if sheet.get("filterMode") == True:
        return True, "Filter mode enabled on Sales sheet."
    return False, f"filterMode is {sheet.get('filterMode')}, expected True."
