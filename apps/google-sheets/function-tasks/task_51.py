import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][0]
    # After deleting column H, there should be no cells in column H with data
    h2 = sheet["cells"].get("H2")
    if h2 is not None and h2.get("value") is not None:
        return False, f"Column H still has data. H2 = {h2.get('value')}"
    # Check that G2 still exists (Total column wasn't deleted)
    g2 = sheet["cells"].get("G2")
    if g2 is None:
        return False, "G2 is missing - wrong column may have been deleted."
    return True, "Column H (Salesperson) deleted from Sales sheet."
