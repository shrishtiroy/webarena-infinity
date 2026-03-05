import requests


# Existing invoice IDs in seed data for Sapphire Bay Resort (con_018)
SEED_INVOICE_IDS = {"inv_013"}  # INV-0054


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Sapphire Bay Resort is con_018
    target_contact_id = "con_018"

    invoices = state.get("invoices", [])
    new_invoice = None
    for inv in invoices:
        if inv.get("contactId") == target_contact_id and inv.get("id") not in SEED_INVOICE_IDS:
            new_invoice = inv
            break

    if new_invoice is None:
        return False, "No new invoice found for Sapphire Bay Resort (con_018)."

    # Check status is not deleted/voided (draft or any active status is fine)
    status = new_invoice.get("status", "")
    if status in ("deleted", "voided"):
        return False, f"New invoice for Sapphire Bay Resort has status '{status}', expected a non-deleted status."

    # Check at least one line item with quantity == 3
    line_items = new_invoice.get("lineItems", [])
    if not line_items:
        return False, "New invoice for Sapphire Bay Resort has no line items."

    found_training = False
    for li in line_items:
        quantity = li.get("quantity", 0)
        unit_price = li.get("unitPrice", 0)
        if quantity == 3 and abs(unit_price - 2200.00) < 10.00:
            found_training = True
            break

    if not found_training:
        items_info = [(li.get("quantity"), li.get("unitPrice")) for li in line_items]
        return False, f"No line item found with quantity=3 and unitPrice approximately $2,200.00 (on-site training). Line items (qty, price): {items_info}."

    return True, f"New invoice '{new_invoice.get('number')}' created for Sapphire Bay Resort with 3 days of on-site training at $2,200/day."
