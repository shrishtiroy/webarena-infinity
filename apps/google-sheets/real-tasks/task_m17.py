import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    nr = state.get("namedRanges", {})
    errors = []
    if nr.get("AllSalaries") != "Employees!D2:D26":
        errors.append(f"AllSalaries is '{nr.get('AllSalaries')}', expected 'Employees!D2:D26'")
    if nr.get("AllStock") != "Inventory!D2:D31":
        errors.append(f"AllStock is '{nr.get('AllStock')}', expected 'Inventory!D2:D31'")
    if errors:
        return False, "; ".join(errors) + f". Named ranges: {nr}"
    return True, "Named ranges 'AllSalaries' (Employees!D2:D26) and 'AllStock' (Inventory!D2:D31) created correctly."
