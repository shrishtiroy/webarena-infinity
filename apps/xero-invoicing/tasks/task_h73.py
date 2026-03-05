import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # Invoices with 'Q1' in reference, awaiting payment:
    # INV-0047 (CN-PROJ-2026-Q1, date 2026-02-01)
    # INV-0050 (ALI-2026-Q1, date 2026-02-12)
    # INV-0055 (TV-Q1-2026, date 2026-02-25) ← latest date
    inv = None
    for i in state.get("invoices", []):
        if i.get("number") == "INV-0055":
            inv = i
            break

    if inv is None:
        return False, "Invoice INV-0055 not found."

    payments = inv.get("payments", [])
    # Seed has 0 payments on INV-0055
    if len(payments) < 1:
        return False, "INV-0055 has no payments. Expected a $3,000 partial payment."

    new_payment_amount = sum(float(p.get("amount", 0)) for p in payments)
    if abs(new_payment_amount - 3000.00) > 50.00:
        return False, (
            f"INV-0055 total payments = ${new_payment_amount:.2f}, expected ~$3,000."
        )

    amount_due = float(inv.get("amountDue", 0))
    expected_due = 41800.00 - 3000.00
    if abs(amount_due - expected_due) > 100.00:
        return False, (
            f"INV-0055 amountDue = ${amount_due:.2f}, expected ~${expected_due:.2f}."
        )

    return True, (
        "INV-0055 (TV-Q1-2026, latest-dated Q1 invoice awaiting payment) "
        "received $3,000 partial payment."
    )
