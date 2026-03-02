import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Existing quote numbers in seed data
    seed_quote_numbers = {
        "QU-0022", "QU-0023", "QU-0024", "QU-0025",
        "QU-0026", "QU-0027", "QU-0028", "QU-0029"
    }

    # Southern Cross Veterinary = con_024
    target_contact_id = "con_024"

    quotes = state.get("quotes", [])
    new_quote = None
    for q in quotes:
        if q.get("number") in seed_quote_numbers:
            continue
        if q.get("contactId") == target_contact_id:
            new_quote = q
            break

    if new_quote is None:
        return False, "No new quote found for Southern Cross Veterinary (con_024)."

    status = new_quote.get("status", "")
    if status != "draft":
        return False, f"New quote '{new_quote.get('number')}' status is '{status}', expected 'draft'."

    line_items = new_quote.get("lineItems", [])
    if len(line_items) < 1:
        return False, f"New quote '{new_quote.get('number')}' has no line items."

    # Check for a line item with quantity 8 and unitPrice ~250.00
    found_match = False
    for li in line_items:
        qty = li.get("quantity", 0)
        price = li.get("unitPrice", 0)
        if qty == 8 and abs(float(price) - 250.00) < 1.00:
            found_match = True
            break

    if not found_match:
        quantities = [li.get("quantity") for li in line_items]
        prices = [li.get("unitPrice") for li in line_items]
        return False, (
            f"No line item found with quantity 8 and unitPrice ~250.00 (CONSULT-HR). "
            f"Found quantities: {quantities}, prices: {prices}."
        )

    return True, (
        f"New quote '{new_quote.get('number')}' created for Southern Cross Veterinary "
        f"with 8 hours of consulting at ~$250.00/hr."
    )
