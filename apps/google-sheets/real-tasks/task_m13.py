import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    inventory_sheet = None
    for s in state["sheets"]:
        if s["name"] == "Inventory":
            inventory_sheet = s
            break
    if inventory_sheet is None:
        return False, f"Inventory sheet not found. Sheet names: {[s['name'] for s in state['sheets']]}"
    rules = inventory_sheet.get("conditionalFormats", [])
    for r in rules:
        if (r.get("type") == "equal_to" and
            str(r.get("value")) == "0" and
            r.get("backgroundColor") == "#ff0000"):
            return True, "Conditional format rule for out-of-stock items (stock==0, red background) found."
    return False, f"No matching conditional format rule found. Rules: {rules}"
