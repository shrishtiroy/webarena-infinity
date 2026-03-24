import requests
from collections import defaultdict


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    errors = []

    sheets = state.get("sheets", [])

    # Get Inventory data
    inv = None
    for s in sheets:
        if s.get("name", "") in ("Inventory", "Stock Management"):
            inv = s
            break
    if inv is None and len(sheets) > 2:
        inv = sheets[2]

    # Find Supplier Summary sheet
    ss = None
    for s in sheets:
        if s.get("name", "").strip() == "Supplier Summary":
            ss = s
            break
    if ss is None:
        return False, f"No sheet named 'Supplier Summary' found. Sheets: {[s['name'] for s in sheets]}"

    ss_cells = ss.get("cells", {})

    # Check headers
    for col, header in [("A", "Supplier"), ("B", "Product Count"), ("C", "Total Stock")]:
        cell = ss_cells.get(f"{col}1", {})
        if str(cell.get("value", "")).strip() != header:
            errors.append(f"{col}1 should be '{header}', got '{cell.get('value', '')}'")
        fmt = cell.get("format", {})
        if not fmt.get("bold"):
            errors.append(f"{col}1 should be bold")
        if str(fmt.get("backgroundColor", "")).lower() != "#cfe2f3":
            errors.append(f"{col}1 bg should be '#cfe2f3'")

    # Compute expected supplier data from Inventory
    if inv:
        inv_cells = inv.get("cells", {})
        supplier_data = defaultdict(lambda: {"count": 0, "stock": 0})
        for r in range(2, 32):
            g_cell = inv_cells.get(f"G{r}")
            d_cell = inv_cells.get(f"D{r}")
            if g_cell and g_cell.get("value"):
                supplier = str(g_cell["value"])
                supplier_data[supplier]["count"] += 1
                if d_cell and isinstance(d_cell.get("value"), (int, float)):
                    supplier_data[supplier]["stock"] += d_cell["value"]

        sorted_suppliers = sorted(supplier_data.keys())
        max_stock = max(v["stock"] for v in supplier_data.values())

        for i, supplier in enumerate(sorted_suppliers):
            row = i + 2
            a_val = str(ss_cells.get(f"A{row}", {}).get("value", "")).strip()
            if a_val != supplier:
                errors.append(f"A{row} should be '{supplier}', got '{a_val}'")

            b_val = ss_cells.get(f"B{row}", {}).get("value")
            expected_count = supplier_data[supplier]["count"]
            if b_val != expected_count and str(b_val) != str(expected_count):
                errors.append(f"B{row} should be {expected_count}, got '{b_val}'")

            c_val = ss_cells.get(f"C{row}", {}).get("value")
            expected_stock = supplier_data[supplier]["stock"]
            if isinstance(c_val, (int, float)):
                if abs(c_val - expected_stock) > 0.01:
                    errors.append(f"C{row} should be {expected_stock}, got {c_val}")
            else:
                errors.append(f"C{row} should be numeric, got '{c_val}'")

            # Check bold on highest stock supplier
            if abs(supplier_data[supplier]["stock"] - max_stock) < 0.01:
                a_cell = ss_cells.get(f"A{row}", {})
                if not a_cell.get("format", {}).get("bold"):
                    errors.append(f"A{row} ({supplier}, highest stock) should be bold")

    if errors:
        return False, "; ".join(errors[:5])
    return True, "Supplier Summary sheet created correctly."
