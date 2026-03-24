import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    nr = state.get("namedRanges", {})
    if nr.get("LowStockItems") == "Inventory!D2:D31":
        return True, "Named range 'LowStockItems' created correctly."
    return False, f"Named ranges: {nr}"
