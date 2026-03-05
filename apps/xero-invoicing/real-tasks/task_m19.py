import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoices = state.get("invoices", [])
    target = None
    for inv in invoices:
        if inv.get("number") == "INV-0045":
            target = inv
            break

    if target is None:
        return False, "Could not find invoice with number 'INV-0045'."

    payments = target.get("payments", [])
    if len(payments) != 0:
        return False, f"Expected payments to be empty after reversal, but found {len(payments)} payment(s)."

    amount_paid = target.get("amountPaid", -1)
    if abs(amount_paid) >= 0.01:
        return False, f"Expected amountPaid to be 0 after reversal, but found {amount_paid}."

    total = target.get("total", 0)
    amount_due = target.get("amountDue", 0)
    if abs(amount_due - 15840.00) >= 0.01:
        return False, f"Expected amountDue to be approximately 15840.00, but found {amount_due}."

    return True, "Partial payment on INV-0045 has been reversed. Payments empty, amountPaid is 0, amountDue is 15840.00."
