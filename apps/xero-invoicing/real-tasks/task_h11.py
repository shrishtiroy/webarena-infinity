import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoices = state.get("invoices", [])
    target = None
    for inv in invoices:
        if inv.get("number") == "INV-0052":
            target = inv
            break

    if target is None:
        return False, "Could not find invoice with number 'INV-0052'."

    # Verify total is approximately 27324.00
    total = target.get("total", 0)
    if abs(total - 27324.00) > 1.00:
        return False, f"Invoice INV-0052 total is {total}, expected approximately 27324.00."

    # Check that at least one payment of approximately $5,000 exists
    payments = target.get("payments", [])
    if not payments:
        return False, "Invoice INV-0052 has no payments recorded."

    found_payment = False
    for payment in payments:
        amount = payment.get("amount", 0)
        if abs(amount - 5000.00) < 100.00:
            found_payment = True
            break

    if not found_payment:
        return False, f"No payment of approximately $5,000 found on INV-0052. Payments: {[p.get('amount') for p in payments]}."

    # Check amountPaid is approximately 5000.00
    amount_paid = target.get("amountPaid", 0)
    if abs(amount_paid - 5000.00) > 100.00:
        return False, f"Invoice INV-0052 amountPaid is {amount_paid}, expected approximately 5000.00."

    # Check amountDue is approximately 22324.00
    amount_due = target.get("amountDue", 0)
    if abs(amount_due - 22324.00) > 100.00:
        return False, f"Invoice INV-0052 amountDue is {amount_due}, expected approximately 22324.00."

    return True, "Invoice INV-0052 (Cascade Software Solutions) has a $5,000 partial payment recorded with correct amountPaid and amountDue."
