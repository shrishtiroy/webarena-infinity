import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Existing invoice numbers in seed data
    seed_invoice_numbers = {
        "INV-0042", "INV-0043", "INV-0044", "INV-0045", "INV-0046",
        "INV-0047", "INV-0048", "INV-0049", "INV-0050", "INV-0051",
        "INV-0052", "INV-0053", "INV-0054", "INV-0055", "INV-0056",
        "INV-0057", "INV-0058", "INV-0059", "INV-0060", "INV-0061",
        "INV-0062", "INV-0063", "INV-0064", "INV-0065", "INV-0066"
    }

    # Wellington & Partners Accounting = con_016
    target_contact_id = "con_016"

    invoices = state.get("invoices", [])
    new_invoice = None
    for inv in invoices:
        if inv.get("number") in seed_invoice_numbers:
            continue
        if inv.get("contactId") == target_contact_id:
            new_invoice = inv
            break

    if new_invoice is None:
        return False, "No new invoice found for Wellington & Partners Accounting (con_016)."

    currency = new_invoice.get("currency", "")
    if currency != "USD":
        return False, f"New invoice '{new_invoice.get('number')}' currency is '{currency}', expected 'USD'."

    line_items = new_invoice.get("lineItems", [])
    if len(line_items) < 1:
        return False, f"New invoice '{new_invoice.get('number')}' has no line items."

    # Check for a line item with quantity 12 and unitPrice ~250.00
    found_match = False
    for li in line_items:
        qty = li.get("quantity", 0)
        price = li.get("unitPrice", 0)
        if qty == 12 and abs(float(price) - 250.00) < 1.00:
            found_match = True
            break

    if not found_match:
        quantities = [li.get("quantity") for li in line_items]
        prices = [li.get("unitPrice") for li in line_items]
        return False, (
            f"No line item found with quantity 12 and unitPrice ~250.00 (CONSULT-HR). "
            f"Found quantities: {quantities}, prices: {prices}."
        )

    return True, (
        f"New invoice '{new_invoice.get('number')}' created for Wellington & Partners "
        f"in USD with 12 hours of consulting at ~$250.00/hr."
    )
