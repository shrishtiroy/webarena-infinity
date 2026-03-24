import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    names = [s["name"] for s in state["sheets"]]
    if len(names) >= 4 and "Employees (Copy)" in names:
        return True, "Employees sheet duplicated."
    return False, f"Sheet names: {names}"
