import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Record full payments via Business Cheque Account for all overdue invoices
    belonging to contacts in the Waikato region."""
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

    # Find Waikato contact IDs
    waikato_ids = set()
    for c in contacts:
        addr = c.get("billingAddress", {})
        if addr.get("region") == "Waikato":
            waikato_ids.add(c.get("id"))

    if not waikato_ids:
        return False, "No Waikato contacts found"

    # No overdue invoices should remain for Waikato contacts
    still_overdue = [
        inv for inv in invoices
        if inv.get("contactId") in waikato_ids and inv.get("status") == "overdue"
    ]
    if still_overdue:
        nums = [inv.get("invoiceNumber") for inv in still_overdue]
        errors.append(f"Overdue invoices still exist for Waikato contacts: {nums}")

    # Verify specific known invoices are paid
    for inv_num in ["INV-0100", "INV-0102"]:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            errors.append(f"{inv_num} not found")
            continue
        if inv.get("status") != "paid":
            errors.append(f"{inv_num} status is '{inv.get('status')}', expected 'paid'")
        if (inv.get("amountDue") or 0) > 0.01:
            errors.append(f"{inv_num} amountDue is {inv.get('amountDue')}, expected <= 0.01")
        inv_payments = [p for p in payments if p.get("invoiceId") == inv.get("id")]
        bank_ids = [p.get("bankAccountId") for p in inv_payments]
        if "bank_1" not in bank_ids:
            errors.append(f"{inv_num} has no payment via bank_1 (Business Cheque)")

    if errors:
        return False, "; ".join(errors)
    return True, "All Waikato overdue invoices paid via Business Cheque Account"
