import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the Sales sheet (index 0)
    if len(state["sheets"]) < 1:
        return False, "Sales sheet not found (no sheets)."
    sheet = state["sheets"][0]

    cell = sheet["cells"].get("H2")
    if cell is None:
        return True, "Cell H2 does not exist on the Sales sheet (cleared)."

    value = cell.get("value")
    if value is None or value == "":
        return True, "Cell H2 on the Sales sheet has been cleared."
    return False, f"Expected H2 to be empty, but found '{value}'."
