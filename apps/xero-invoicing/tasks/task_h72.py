import requests


SEED_INVOICE_IDS = {
    "inv_000", "inv_001", "inv_002", "inv_003", "inv_004", "inv_005",
    "inv_006", "inv_007", "inv_008", "inv_009", "inv_010", "inv_011",
    "inv_012", "inv_013", "inv_014", "inv_015", "inv_016", "inv_017",
    "inv_018", "inv_019", "inv_020", "inv_021", "inv_022", "inv_023",
    "inv_024", "inv_025",
}


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # INV-0046 (Baxter & Associates, con_005) should be fully paid
    inv_0046 = None
    for i in state.get("invoices", []):
        if i.get("number") == "INV-0046":
            inv_0046 = i
            break

    if inv_0046 is None:
        return False, "Invoice INV-0046 not found."

    if inv_0046.get("status") != "paid":
        return False, (
            f"INV-0046 status is '{inv_0046.get('status')}', expected 'paid'."
        )

    # New invoice for Baxter (con_005) with Professional Services theme
    new_inv = None
    for inv in state.get("invoices", []):
        if inv.get("contactId") == "con_005" and inv.get("id") not in SEED_INVOICE_IDS:
            new_inv = inv
            break

    if new_inv is None:
        return False, (
            "No new invoice found for Baxter & Associates Legal (con_005)."
        )

    # Should be submitted for approval (awaiting_approval), NOT approved
    status = new_inv.get("status", "")
    if status != "awaiting_approval":
        return False, (
            f"New invoice status is '{status}', expected 'awaiting_approval'. "
            f"The invoice should be submitted for approval, not approved."
        )

    theme = new_inv.get("brandingThemeId", "")
    if theme != "theme_professional":
        return False, (
            f"New invoice brandingThemeId is '{theme}', expected 'theme_professional'."
        )

    # Check line item: 8 hours dev at ~$185
    line_items = new_inv.get("lineItems", [])
    found = False
    for li in line_items:
        price = float(li.get("unitPrice", 0))
        qty = li.get("quantity", 0)
        if abs(price - 185.00) < 10.00 and qty == 8:
            found = True
            break

    if not found:
        items = [(li.get("unitPrice"), li.get("quantity")) for li in line_items]
        return False, (
            f"No line item with qty 8 and unitPrice ~$185 (development) found. "
            f"Items: {items}."
        )

    return True, (
        f"INV-0046 paid in full. New invoice '{new_inv.get('number')}' for Baxter & Associates "
        f"(8 hrs dev, Professional Services) submitted for approval."
    )
