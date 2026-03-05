import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find quote QU-0029 (Alpha Logistics International, con_012)
    quotes = state.get("quotes", [])
    quote = None
    for q in quotes:
        if q.get("number") == "QU-0029":
            quote = q
            break

    if quote is None:
        return False, "Quote QU-0029 not found."

    if not quote.get("isInvoiced"):
        return False, f"Quote QU-0029 isInvoiced is {quote.get('isInvoiced')}, expected True."

    # Existing invoice numbers in seed data
    seed_invoice_numbers = {
        "INV-0042", "INV-0043", "INV-0044", "INV-0045", "INV-0046",
        "INV-0047", "INV-0048", "INV-0049", "INV-0050", "INV-0051",
        "INV-0052", "INV-0053", "INV-0054", "INV-0055", "INV-0056",
        "INV-0057", "INV-0058", "INV-0059", "INV-0060", "INV-0061",
        "INV-0062", "INV-0063", "INV-0064", "INV-0065", "INV-0066"
    }

    # Alpha Logistics International = con_012
    target_contact_id = "con_012"

    invoices = state.get("invoices", [])
    new_invoice = None
    for inv in invoices:
        if inv.get("number") in seed_invoice_numbers:
            continue
        if inv.get("contactId") == target_contact_id:
            new_invoice = inv
            break

    if new_invoice is None:
        return False, "No new invoice found for Alpha Logistics International (con_012)."

    if new_invoice.get("status") != "draft":
        return False, (
            f"New invoice '{new_invoice.get('number')}' status is '{new_invoice.get('status')}', "
            f"expected 'draft'."
        )

    line_items = new_invoice.get("lineItems", [])
    if len(line_items) < 1:
        return False, f"New invoice '{new_invoice.get('number')}' has no line items."

    return True, (
        f"Quote QU-0029 marked as invoiced and new draft invoice "
        f"'{new_invoice.get('number')}' created for Alpha Logistics International "
        f"with {len(line_items)} line item(s)."
    )
