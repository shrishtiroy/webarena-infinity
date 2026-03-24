import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    cells = sheet.get("cells", {})
    # Check that H1 header is not "Salesperson"
    h1 = cells.get("H1")
    if h1 and h1.get("value") == "Salesperson":
        return False, "Header 'Salesperson' still exists in H1. Column was not removed."
    # Check that known salesperson names no longer appear anywhere in the sheet
    known_salespeople = ["Alex Rivera", "Jordan Kim", "Casey Chen", "Morgan Park", "Taylor Singh"]
    for addr, cell in cells.items():
        v = cell.get("value")
        if v in known_salespeople:
            return False, f"Salesperson name '{v}' still found in cell {addr}. Column was not fully removed."
    return True, "Salesperson column removed from Sales sheet. No salesperson names or header found."
