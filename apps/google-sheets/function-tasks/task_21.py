import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheets = state["sheets"]
    if len(sheets) >= 4:
        return True, f"New sheet added. Total sheets: {len(sheets)}."
    return False, f"Expected at least 4 sheets, got {len(sheets)}."
