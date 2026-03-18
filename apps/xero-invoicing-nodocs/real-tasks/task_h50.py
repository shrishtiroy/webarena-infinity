import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Create Fiordland Adventures Ltd contact, create invoice with 2 line items,
    approve and send, then record $2,000 partial payment."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    contacts = state.get("contacts", [])
    invoices = state.get("invoices", [])
    payments = state.get("payments", [])
    errors = []

    # Find contact
    contact = next(
        (c for c in contacts if c.get("name") == "Fiordland Adventures Ltd"),
        None,
    )
    if contact is None:
        return False, "Contact 'Fiordland Adventures Ltd' not found"

    contact_id = contact.get("id")

    # Verify contact fields
    if contact.get("email") != "bookings@fiordland.co.nz":
        errors.append(f"email is '{contact.get('email')}', expected 'bookings@fiordland.co.nz'")
    if contact.get("phone") != "+64 3 249 8000":
        errors.append(f"phone is '{contact.get('phone')}', expected '+64 3 249 8000'")
    if contact.get("taxId") != "NZ-88-222-333":
        errors.append(f"taxId is '{contact.get('taxId')}', expected 'NZ-88-222-333'")

    addr = contact.get("billingAddress", {}) or {}
    expected_addr = {
        "street": "36 Town Centre",
        "city": "Te Anau",
        "region": "Southland",
        "postalCode": "9600",
        "country": "New Zealand",
    }
    for field, val in expected_addr.items():
        actual = (addr.get(field) or "").strip()
        if actual != val:
            errors.append(f"billingAddress.{field} is '{actual}', expected '{val}'")

    # Find invoice for this contact
    inv = next(
        (i for i in invoices if i.get("contactId") == contact_id),
        None,
    )
    if inv is None:
        errors.append("No invoice found for Fiordland Adventures Ltd")
        return False, "; ".join(errors)

    # Status should be awaiting_payment (approved, sent, partially paid but not fully)
    if inv.get("status") != "awaiting_payment":
        errors.append(f"Invoice status is '{inv.get('status')}', expected 'awaiting_payment'")

    # Should have sentAt
    if not inv.get("sentAt"):
        errors.append("Invoice has no sentAt timestamp")

    # Check line items
    line_items = inv.get("lineItems", [])
    if len(line_items) != 2:
        errors.append(f"Invoice has {len(line_items)} line items, expected 2")

    tour = next((li for li in line_items if "tour" in (li.get("description") or "").lower()), None)
    if tour is None:
        errors.append("No line item with description containing 'tour'")
    else:
        if tour.get("quantity") != 12:
            errors.append(f"Tour qty is {tour.get('quantity')}, expected 12")
        if abs((tour.get("unitPrice") or 0) - 350) > 0.01:
            errors.append(f"Tour unitPrice is {tour.get('unitPrice')}, expected 350")

    equip = next((li for li in line_items if "equipment" in (li.get("description") or "").lower()), None)
    if equip is None:
        errors.append("No line item with description containing 'equipment'")
    else:
        if equip.get("quantity") != 5:
            errors.append(f"Equipment qty is {equip.get('quantity')}, expected 5")
        if abs((equip.get("unitPrice") or 0) - 120) > 0.01:
            errors.append(f"Equipment unitPrice is {equip.get('unitPrice')}, expected 120")

    # Check dates, reference
    if inv.get("issueDate") != "2026-03-18":
        errors.append(f"issueDate is '{inv.get('issueDate')}', expected '2026-03-18'")
    if inv.get("dueDate") != "2026-05-17":
        errors.append(f"dueDate is '{inv.get('dueDate')}', expected '2026-05-17'")
    if inv.get("reference") != "FIOR-2026-001":
        errors.append(f"reference is '{inv.get('reference')}', expected 'FIOR-2026-001'")

    # Check $2,000 partial payment
    inv_payments = [p for p in payments if p.get("invoiceId") == inv.get("id")]
    if not inv_payments:
        errors.append("No payment recorded on the invoice")
    else:
        total_paid = sum(p.get("amount", 0) for p in inv_payments)
        if abs(total_paid - 2000) > 0.01:
            errors.append(f"Total paid is ${total_paid}, expected $2,000")
        bank_ids = [p.get("bankAccountId") for p in inv_payments]
        if "bank_1" not in bank_ids:
            errors.append("No payment via bank_1 (Business Cheque Account)")

    if abs((inv.get("amountPaid") or 0) - 2000) > 0.01:
        errors.append(f"amountPaid is {inv.get('amountPaid')}, expected 2000")

    if errors:
        return False, "; ".join(errors)
    return True, "Fiordland Adventures Ltd created, invoice approved, sent, and $2,000 partial payment recorded"
