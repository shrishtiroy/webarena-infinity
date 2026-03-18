import requests


def verify(server_url: str) -> tuple[bool, str]:
    """For each contact with exactly two overdue invoices, void the one with
    the lower total and pay the one with the higher total via Business Cheque."""
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

    # Contacts with exactly 2 overdue in seed data:
    # Bloom & Branch Florists: INV-0015 ($35,937.50) lower → void, INV-0040 ($121,725) higher → pay
    # Pacific Timber Supplies: INV-0039 ($4,027.50) lower → void, INV-0089 ($5,209) higher → pay
    # Nexus Technologies Ltd: INV-0079 ($6,603.88) lower → void, INV-0104 ($7,038) higher → pay

    expected_voided = ["INV-0015", "INV-0039", "INV-0079"]
    expected_paid = ["INV-0040", "INV-0089", "INV-0104"]

    for inv_num in expected_voided:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            errors.append(f"{inv_num} not found")
        elif inv.get("status") != "voided":
            errors.append(f"{inv_num} (lower total) status is '{inv.get('status')}', expected 'voided'")

    for inv_num in expected_paid:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            errors.append(f"{inv_num} not found")
            continue
        if inv.get("status") != "paid":
            errors.append(f"{inv_num} (higher total) status is '{inv.get('status')}', expected 'paid'")
        if (inv.get("amountDue") or 0) > 0.01:
            errors.append(f"{inv_num} amountDue is {inv.get('amountDue')}, expected <= 0.01")
        inv_payments = [p for p in payments if p.get("invoiceId") == inv.get("id")]
        bank_ids = [p.get("bankAccountId") for p in inv_payments]
        if "bank_1" not in bank_ids:
            errors.append(f"{inv_num} has no payment via bank_1")

    if errors:
        return False, "; ".join(errors)
    return True, "For all contacts with 2 overdue: lower-total voided, higher-total paid"
