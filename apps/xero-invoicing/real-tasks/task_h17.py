import requests


# Existing invoice IDs in seed data for Outback Adventures Tourism (con_015)
SEED_INVOICE_IDS = {"inv_024"}  # INV-0065 (voided)


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Outback Adventures Tourism is con_015
    target_contact_id = "con_015"

    invoices = state.get("invoices", [])
    new_invoice = None
    for inv in invoices:
        if inv.get("contactId") == target_contact_id and inv.get("id") not in SEED_INVOICE_IDS:
            new_invoice = inv
            break

    if new_invoice is None:
        return False, "No new invoice found for Outback Adventures Tourism (con_015)."

    # Check at least 2 line items
    line_items = new_invoice.get("lineItems", [])
    if len(line_items) < 2:
        return False, f"New invoice has {len(line_items)} line item(s), expected at least 2."

    # Check one line item has unitPrice approximately 5500.00 (AUDIT - security audit)
    found_audit = False
    found_data_mig = False
    for li in line_items:
        unit_price = li.get("unitPrice", 0)
        if abs(unit_price - 5500.00) < 10.00:
            found_audit = True
        if abs(unit_price - 3800.00) < 10.00:
            found_data_mig = True

    if not found_audit:
        prices = [li.get("unitPrice") for li in line_items]
        return False, f"No line item with unitPrice approximately $5,500.00 (security audit) found. Prices: {prices}."

    if not found_data_mig:
        prices = [li.get("unitPrice") for li in line_items]
        return False, f"No line item with unitPrice approximately $3,800.00 (data migration) found. Prices: {prices}."

    return True, f"New invoice '{new_invoice.get('number')}' created for Outback Adventures Tourism with security audit ($5,500) and data migration ($3,800) line items."
