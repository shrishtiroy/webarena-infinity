import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    names = [s["name"] for s in state["sheets"]]
    if "Stock Levels" in names and "Inventory" not in names:
        return True, "Inventory renamed to 'Stock Levels'."
    return False, f"Sheet names: {names}"
