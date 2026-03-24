import requests

def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    nr = state.get("namedRanges", {})
    if nr.get("EmployeeSalaries") == "Employees!D2:D26":
        return True, "Named range 'EmployeeSalaries' created correctly."
    return False, f"Named ranges: {nr}"
