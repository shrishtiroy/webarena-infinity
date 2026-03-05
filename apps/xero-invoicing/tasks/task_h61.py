import requests


def verify(server_url: str) -> tuple[bool, str]:
    resp = requests.get(f"{server_url}/api/state")
    if resp.status_code != 200:
        return False, "Could not retrieve application state."
    state = resp.json()

    # The client with both an active repeating invoice and an open credit note is
    # CloudNine Analytics (con_007): active rep_002 + open CN-0012.
    # Their oldest unpaid invoice is INV-0047 (due 2026-02-15).
    inv = None
    for i in state.get("invoices", []):
        if i.get("number") == "INV-0047":
            inv = i
            break

    if inv is None:
        return False, "Invoice INV-0047 not found."

    payments = inv.get("payments", [])
    # Seed has 0 payments on INV-0047; we expect at least one new payment
    if len(payments) < 1:
        return False, f"INV-0047 has no payments. Expected a $1,000 partial payment."

    total_paid = sum(float(p.get("amount", 0)) for p in payments)
    if abs(total_paid - 1000.00) > 50.00:
        return False, (
            f"INV-0047 total payments = ${total_paid:.2f}, expected ~$1,000."
        )

    amount_due = float(inv.get("amountDue", 0))
    expected_due = 18652.70 - 1000.00
    if abs(amount_due - expected_due) > 100.00:
        return False, (
            f"INV-0047 amountDue = ${amount_due:.2f}, expected ~${expected_due:.2f}."
        )

    return True, (
        "CloudNine Analytics (active repeating invoice + open credit note) identified. "
        "$1,000 partial payment recorded on INV-0047 (oldest unpaid)."
    )
