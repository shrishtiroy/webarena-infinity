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

    # Look up Amara Okafor by scanning column A
    target_row = None
    for addr, cell in sheet["cells"].items():
        if addr.startswith("A") and cell.get("value") == "Amara Okafor":
            row = addr[1:]
            target_row = row
            break

    if target_row is None:
        return False, "Amara Okafor not found on the Employees sheet."

    status_cell = sheet["cells"].get(f"G{target_row}")
    if status_cell is None:
        return False, f"No status cell found at G{target_row}."

    status_value = status_cell.get("value")
    if status_value == "Active":
        return True, "Amara Okafor's status is correctly set to 'Active'."
    return False, f"Expected Amara Okafor's status to be 'Active', but found '{status_value}'."
