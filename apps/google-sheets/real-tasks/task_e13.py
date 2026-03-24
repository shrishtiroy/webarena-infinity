import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Verify that the Laptop Pro 15 product name is underlined on the Inventory sheet."""
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
        if addr.startswith("B") and cell.get("value") == "Laptop Pro 15":
            target_row = addr[1:]
            break

    if target_row is None:
        return False, "Could not find 'Laptop Pro 15' in column B of the Inventory sheet."

    cell_addr = f"B{target_row}"
    cell = cells.get(cell_addr, {})
    fmt = cell.get("format", {})
    underline = fmt.get("underline", False)

    if underline is True:
        return True, f"Cell {cell_addr} ('Laptop Pro 15') has underline formatting applied."

    return False, f"Cell {cell_addr} ('Laptop Pro 15') does not have underline formatting. Format: {fmt}"
