import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Remove partial payment from INV-0034, then record full payment for the
    total amount via Business Cheque Account."""
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

    inv = next((i for i in invoices if i.get("invoiceNumber") == "INV-0034"), None)
    if inv is None:
        return False, "INV-0034 not found"

    # Check invoice is fully paid
    if inv.get("status") != "paid":
        errors.append(f"status is '{inv.get('status')}', expected 'paid'")
    if (inv.get("amountDue") or 0) > 0.01:
        errors.append(f"amountDue is {inv.get('amountDue')}, expected <= 0.01")

    inv_id = inv.get("id")
    inv_payments = [p for p in payments if p.get("invoiceId") == inv_id]

    # The old partial payment (pay_14, amount $4128.54) should be removed
    old_partial = [p for p in inv_payments if abs((p.get("amount") or 0) - 4128.54) < 0.01]
    if old_partial:
        errors.append("Old partial payment ($4128.54) still exists — should have been removed")

    # Should have a payment for the full total ($6517.50) via bank_1
    total = inv.get("total", 0)
    full_payment = [
        p for p in inv_payments
        if p.get("bankAccountId") == "bank_1"
        and abs((p.get("amount") or 0) - total) < 0.01
    ]
    if not full_payment:
        errors.append(
            f"No payment found for full total (${total}) via bank_1. "
            f"Existing payments: {[(p.get('amount'), p.get('bankAccountId')) for p in inv_payments]}"
        )

    if errors:
        return False, "; ".join(errors)
    return True, "INV-0034 partial payment removed and full payment recorded via Business Cheque"
