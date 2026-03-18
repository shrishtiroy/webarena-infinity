import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Record a full payment via the Business Cheque Account for the overdue
    invoice with the lowest total amount."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    payments = state.get("payments", [])
    errors = []

    # The lowest-total overdue invoice in seed data is INV-0068 ($431.25)
    target = next((i for i in invoices if i.get("invoiceNumber") == "INV-0068"), None)
    if target is None:
        return False, "INV-0068 not found"

    if target.get("status") != "paid":
        errors.append(f"INV-0068 status is '{target.get('status')}', expected 'paid'")

    if (target.get("amountDue") or 0) > 0.01:
        errors.append(f"INV-0068 amountDue is {target.get('amountDue')}, expected <= 0.01")

    inv_payments = [p for p in payments if p.get("invoiceId") == target.get("id")]
    bank_ids = [p.get("bankAccountId") for p in inv_payments]
    if "bank_1" not in bank_ids:
        errors.append("INV-0068 has no payment via bank_1 (Business Cheque Account)")

    if errors:
        return False, "; ".join(errors)
    return True, "INV-0068 (lowest overdue total $431.25) fully paid via Business Cheque Account"
