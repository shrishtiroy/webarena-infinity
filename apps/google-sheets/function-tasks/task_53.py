import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    has_north = False
    has_northern = False
    for r in range(2, 42):
        cell = sheet["cells"].get(f"D{r}")
        if cell:
            v = cell.get("value")
            if v == "North":
                has_north = True
            if v == "Northern":
                has_northern = True
    if has_north:
        return False, "Still found 'North' in column D."
    if not has_northern:
        return False, "No 'Northern' found in column D."
    return True, "All 'North' replaced with 'Northern' in Sales."
