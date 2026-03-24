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

    # Find item with highest unit cost
    max_cost = -1
    max_supplier = None
    for r in range(2, 32):
        f_cell = cells.get(f"F{r}")
        if f_cell and isinstance(f_cell.get("value"), (int, float)):
            if f_cell["value"] > max_cost:
                max_cost = f_cell["value"]
                g_cell = cells.get(f"G{r}", {})
                max_supplier = str(g_cell.get("value", ""))

    if not max_supplier:
        return False, "Could not determine highest-cost item's supplier."

    # Check all supplier cells for that supplier have yellow bg
    for r in range(2, 32):
        g_cell = cells.get(f"G{r}")
        if g_cell and str(g_cell.get("value", "")) == max_supplier:
            bg = str(g_cell.get("format", {}).get("backgroundColor", "")).lower()
            if bg != "#fff2cc":
                errors.append(
                    f"G{r} (supplier '{max_supplier}') bg should be '#fff2cc', got '{bg}'"
                )

    # Check named range
    named = state.get("namedRanges", {})
    if "PremiumSupplier" not in named:
        errors.append("Named range 'PremiumSupplier' not found")
    elif named["PremiumSupplier"] != "Inventory!G2:G31":
        errors.append(
            f"PremiumSupplier should be 'Inventory!G2:G31', got '{named['PremiumSupplier']}'"
        )

    if errors:
        return False, "; ".join(errors[:5])
    return True, f"Supplier '{max_supplier}' highlighted correctly with named range."
