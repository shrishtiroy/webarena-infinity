import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    if state["activeSheet"] == 1:
        return True, "Active sheet is Employees (index 1)."
    return False, f"Active sheet is {state['activeSheet']}, expected 1."
