import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    cell = sheet["cells"].get("A1")
    if not cell:
        return False, "Cell A1 not found."
    fmt = cell.get("format", {})
    borders = ["borderTop", "borderBottom", "borderLeft", "borderRight"]
    all_set = all(fmt.get(b) and len(str(fmt.get(b))) > 0 for b in borders)
    if all_set:
        return True, "All borders applied to A1."
    missing = [b for b in borders if not fmt.get(b)]
    return False, f"Missing borders: {missing}. Format: {fmt}"
