import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Record full payment via Business Cheque Account for every overdue
    invoice belonging to contacts who have exactly one overdue invoice."""
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

    # Known invoices for contacts with exactly 1 overdue in seed data:
    # Metro Print (INV-0033), Pinnacle (INV-0059), Harmony Music (INV-0063),
    # Apex Legal (INV-0068), Swift Courier (INV-0087), Velocity Sports (INV-0100),
    # Hamilton Plumbing (INV-0102), Green Valley (INV-0107)
    expected_paid = [
        "INV-0033", "INV-0059", "INV-0063", "INV-0068",
        "INV-0087", "INV-0100", "INV-0102", "INV-0107",
    ]

    for inv_num in expected_paid:
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
            errors.append(f"{inv_num} has no payment via bank_1")

    # Contacts with 2+ overdue (Bloom & Branch, Pacific Timber, Nexus) should still have overdue
    multi_overdue_nums = ["INV-0015", "INV-0040", "INV-0039", "INV-0089", "INV-0079", "INV-0104"]
    for inv_num in multi_overdue_nums:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            continue
        if inv.get("status") == "paid":
            errors.append(f"{inv_num} should NOT be paid (contact has multiple overdue invoices)")

    if errors:
        return False, "; ".join(errors)
    return True, f"All {len(expected_paid)} invoices for single-overdue contacts paid via Business Cheque"
