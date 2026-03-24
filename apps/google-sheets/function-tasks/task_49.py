import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    cell = sheet["cells"].get("A2")
    if cell and cell.get("value") == "01/12/2024":
        return True, "Row 2 deleted. New A2 is '01/12/2024'."
    return False, f"Expected A2 '01/12/2024', got '{cell.get('value') if cell else 'no cell'}'."
