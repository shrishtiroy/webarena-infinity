import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])
    inv = None
    for s in sheets:
        if s.get("name", "") in ("Inventory", "Stock Management"):
            inv = s
            break
    if inv is None and len(sheets) > 2:
        inv = sheets[2]
    if inv is None:
        return False, "Inventory sheet not found."

    cells = inv.get("cells", {})

    # Use bold product name as the indicator that an item was restocked.
    # Seed data has no bold on product name cells, so bold = restocked by the task.
    restocked_count = 0
    for r in range(2, 32):
        d_cell = cells.get(f"D{r}")
        e_cell = cells.get(f"E{r}")
        b_cell = cells.get(f"B{r}")
        if not d_cell or not e_cell or not b_cell:
            continue

        stock = d_cell.get("value", 0)
        reorder = e_cell.get("value", 0)
        if not isinstance(stock, (int, float)) or not isinstance(reorder, (int, float)):
            continue

        is_bold = b_cell.get("format", {}).get("bold", False)

        # Items still below reorder should have been restocked
        if stock < reorder:
            product = b_cell.get("value", "")
            errors.append(
                f"D{r} ({product}) stock {stock} < reorder {reorder}: "
                f"should have been restocked to {2 * reorder}"
            )

        # Bold items were restocked - verify stock == 2*reorder
        if is_bold:
            restocked_count += 1
            expected = 2 * reorder
            if stock != expected:
                product = b_cell.get("value", "")
                errors.append(
                    f"D{r} ({product}) restocked stock should be {expected}, got {stock}"
                )

    # Check A32 label
    a32 = cells.get("A32", {})
    if str(a32.get("value", "")).strip() != "Items Restocked":
        errors.append(f"A32 should be 'Items Restocked', got '{a32.get('value', '')}'")
    if not a32.get("format", {}).get("bold"):
        errors.append("A32 should be bold")

    # Check B32 count
    b32 = cells.get("B32", {})
    b32_val = b32.get("value")
    if isinstance(b32_val, (int, float)):
        b32_val = int(b32_val)
    if b32_val != restocked_count:
        errors.append(f"B32 should be {restocked_count}, got '{b32_val}'")

    if errors:
        return False, "; ".join(errors[:5])
    return True, f"Stock correction applied to {restocked_count} items."
