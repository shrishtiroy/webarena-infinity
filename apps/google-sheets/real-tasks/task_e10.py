import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the Inventory sheet (index 2)
    if len(state["sheets"]) < 3:
        return False, "Inventory sheet not found (not enough sheets)."
    sheet = state["sheets"][2]

    # Look up Wireless Charger Pad by scanning column B
    target_row = None
    for addr, cell in sheet["cells"].items():
        if addr.startswith("B") and cell.get("value") == "Wireless Charger Pad":
            row = addr[1:]
            target_row = row
            break

    if target_row is None:
        return False, "Wireless Charger Pad not found on the Inventory sheet."

    stock_cell = sheet["cells"].get(f"D{target_row}")
    if stock_cell is None:
        return False, f"No stock cell found at D{target_row}."

    stock_value = stock_cell.get("value")
    # Accept both int 50 and string "50"
    if stock_value == 50 or stock_value == "50":
        return True, "Wireless Charger Pad stock is correctly set to 50."
    return False, f"Expected Wireless Charger Pad stock to be 50, but found '{stock_value}'."
