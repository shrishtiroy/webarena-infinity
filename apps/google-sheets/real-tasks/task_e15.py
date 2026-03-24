import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Wireless Charger Pad name has strikethrough on the Inventory sheet."""
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    sheets = state.get("sheets", [])
    if len(sheets) < 3:
        return False, "Expected at least 3 sheets but found fewer."

    inventory_sheet = sheets[2]
    cells = inventory_sheet.get("cells", {})

    target_row = None
    for addr, cell in cells.items():
        if addr.startswith("B") and cell.get("value") == "Wireless Charger Pad":
            target_row = addr[1:]
            break

    if target_row is None:
        return False, "Could not find 'Wireless Charger Pad' in column B of the Inventory sheet."

    cell_addr = f"B{target_row}"
    cell = cells.get(cell_addr, {})
    fmt = cell.get("format", {})
    strikethrough = fmt.get("strikethrough", False)

    if strikethrough is True:
        return True, f"Cell {cell_addr} ('Wireless Charger Pad') has strikethrough formatting applied."

    return False, f"Cell {cell_addr} ('Wireless Charger Pad') does not have strikethrough formatting. Format: {fmt}"
