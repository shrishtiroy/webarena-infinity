import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    if state["sheets"][0]["name"] == "Inventory":
        return True, "Inventory sheet moved to first position."
    return False, f"First sheet is '{state['sheets'][0]['name']}', expected 'Inventory'."
