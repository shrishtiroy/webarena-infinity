import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][1]
    has_active = False
    has_current = False
    for r in range(2, 27):
        cell = sheet["cells"].get(f"G{r}")
        if cell:
            v = cell.get("value")
            if v == "Active":
                has_active = True
            if v == "Current":
                has_current = True
    if has_active:
        return False, "Still found 'Active' in column G."
    if not has_current:
        return False, "No 'Current' found in column G."
    return True, "All 'Active' replaced with 'Current' in Employees."
