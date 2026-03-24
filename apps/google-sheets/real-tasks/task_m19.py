import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()
    sheet = state["sheets"][2]
    cells = sheet.get("cells", {})
    # Collect column B values from row 2 onward
    product_names = []
    for r in range(2, 100):
        cell = cells.get(f"B{r}")
        if cell and cell.get("value") is not None and str(cell.get("value")).strip() != "":
            product_names.append((r, str(cell.get("value"))))
        else:
            break
    if len(product_names) < 2:
        return False, f"Found fewer than 2 product names in column B. Found: {product_names}"
    # Verify ascending alphabetical order (case-insensitive)
    for i in range(len(product_names) - 1):
        current = product_names[i][1].lower()
        next_val = product_names[i + 1][1].lower()
        if current > next_val:
            return False, (
                f"Inventory not sorted alphabetically by product name. "
                f"'{product_names[i][1]}' (row {product_names[i][0]}) comes before "
                f"'{product_names[i + 1][1]}' (row {product_names[i + 1][0]})."
            )
    return True, f"Inventory sheet sorted alphabetically by product name. {len(product_names)} products in correct order."
