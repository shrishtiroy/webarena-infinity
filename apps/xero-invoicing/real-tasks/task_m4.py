import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Find the quote QU-0022
    quotes = state.get("quotes", [])
    quote = None
    for q in quotes:
        if q.get("number") == "QU-0022":
            quote = q
            break

    if quote is None:
        return False, "Quote QU-0022 not found."

    if not quote.get("isInvoiced"):
        return False, f"Quote QU-0022 isInvoiced is {quote.get('isInvoiced')}, expected True."

    quote_contact = quote.get("contactId")
    if quote_contact != "con_001":
        return False, f"Quote QU-0022 contactId is '{quote_contact}', expected 'con_001'."

    # Find a new draft invoice for the same contactId (con_001)
    invoices = state.get("invoices", [])
    new_invoice = None
    for i in invoices:
        if i.get("contactId") == "con_001" and i.get("status") == "draft":
            new_invoice = i
            break

    if new_invoice is None:
        return False, "No new draft invoice found for contactId 'con_001' (Pinnacle Construction)."

    return True, f"Quote QU-0022 has been converted to draft invoice '{new_invoice.get('number')}'."
