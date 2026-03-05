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

    # Most expensive sent quote: QU-0024 ($76,725, Atlas Engineering, con_025)
    quo = None
    for q in state.get("quotes", []):
        if q.get("number") == "QU-0024":
            quo = q
            break

    if quo is None:
        return False, "Quote QU-0024 not found."

    if quo.get("status") != "declined":
        return False, (
            f"QU-0024 status is '{quo.get('status')}', expected 'declined'."
        )

    # New invoice for Atlas Engineering (con_025)
    new_inv = None
    for inv in state.get("invoices", []):
        if inv.get("contactId") == "con_025" and inv.get("id") not in SEED_INVOICE_IDS:
            new_inv = inv
            break

    if new_inv is None:
        return False, (
            "No new invoice found for Atlas Engineering Consultants (con_025)."
        )

    if new_inv.get("status") != "awaiting_payment":
        return False, (
            f"New invoice status is '{new_inv.get('status')}', expected 'awaiting_payment' "
            f"(approved)."
        )

    # Check line item: 5 hours consulting at ~$250
    line_items = new_inv.get("lineItems", [])
    found = False
    for li in line_items:
        price = float(li.get("unitPrice", 0))
        qty = li.get("quantity", 0)
        if abs(price - 250.00) < 10.00 and qty == 5:
            found = True
            break

    if not found:
        items = [(li.get("unitPrice"), li.get("quantity")) for li in line_items]
        return False, (
            f"No line item with qty 5 and unitPrice ~$250 (consulting) found. "
            f"Items: {items}."
        )

    return True, (
        f"QU-0024 (most expensive sent quote, $76,725) declined. "
        f"New invoice '{new_inv.get('number')}' for Atlas Engineering "
        f"(5 hrs consulting) approved."
    )
