import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    invoices = state.get("invoices", [])
    inv = None
    for i in invoices:
        if i.get("number") == "INV-0053":
            inv = i
            break

    if inv is None:
        return False, "Invoice INV-0053 not found."

    if inv.get("status") != "paid":
        return False, f"Invoice INV-0053 status is '{inv.get('status')}', expected 'paid'."

    amount_due = inv.get("amountDue", None)
    if amount_due is None:
        return False, "Invoice INV-0053 has no amountDue field."
    if abs(float(amount_due)) >= 0.01:
        return False, f"Invoice INV-0053 amountDue is {amount_due}, expected 0."

    amount_paid = inv.get("amountPaid", None)
    if amount_paid is None:
        return False, "Invoice INV-0053 has no amountPaid field."
    if abs(float(amount_paid) - 823.90) >= 0.01:
        return False, f"Invoice INV-0053 amountPaid is {amount_paid}, expected approximately 823.90."

    return True, "Invoice INV-0053 (Vanguard Security Systems) has been paid in full."
