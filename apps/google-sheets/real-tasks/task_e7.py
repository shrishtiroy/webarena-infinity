import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the Employees sheet (index 1)
    if len(state["sheets"]) < 2:
        return False, "Employees sheet not found (not enough sheets)."
    sheet = state["sheets"][1]

    # Look up Priya Sharma by scanning column A
    target_row = None
    for addr, cell in sheet["cells"].items():
        if addr.startswith("A") and cell.get("value") == "Priya Sharma":
            row = addr[1:]
            target_row = row
            break

    if target_row is None:
        return False, "Priya Sharma not found on the Employees sheet."

    name_cell = sheet["cells"].get(f"A{target_row}")
    if name_cell is None:
        return False, f"No cell found at A{target_row}."

    fmt = name_cell.get("format", {})
    if fmt.get("bold") is True:
        return True, "Priya Sharma's name cell is bold."
    return False, f"Expected Priya Sharma's name cell to be bold, but format is: {fmt}."
