import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Pay all AUD overdue via AUD Holding Account. Pay all NZD overdue > $10k
    via Business Cheque Account."""
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

    # AUD overdue → paid via bank_4: INV-0033, INV-0102
    aud_nums = ["INV-0033", "INV-0102"]
    for inv_num in aud_nums:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            errors.append(f"{inv_num} not found")
            continue
        if inv.get("status") != "paid":
            errors.append(f"{inv_num} (AUD) status is '{inv.get('status')}', expected 'paid'")
        if (inv.get("amountDue") or 0) > 0.01:
            errors.append(f"{inv_num} amountDue is {inv.get('amountDue')}, expected <= 0.01")
        inv_payments = [p for p in payments if p.get("invoiceId") == inv.get("id")]
        bank_ids = [p.get("bankAccountId") for p in inv_payments]
        if "bank_4" not in bank_ids:
            errors.append(f"{inv_num} has no payment via bank_4 (AUD Holding Account)")

    # NZD overdue > $10k → paid via bank_1: INV-0015, INV-0040, INV-0059, INV-0063, INV-0100
    nzd_high_nums = ["INV-0015", "INV-0040", "INV-0059", "INV-0063", "INV-0100"]
    for inv_num in nzd_high_nums:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            errors.append(f"{inv_num} not found")
            continue
        if inv.get("status") != "paid":
            errors.append(f"{inv_num} (NZD > $10k) status is '{inv.get('status')}', expected 'paid'")
        if (inv.get("amountDue") or 0) > 0.01:
            errors.append(f"{inv_num} amountDue is {inv.get('amountDue')}, expected <= 0.01")
        inv_payments = [p for p in payments if p.get("invoiceId") == inv.get("id")]
        bank_ids = [p.get("bankAccountId") for p in inv_payments]
        if "bank_1" not in bank_ids:
            errors.append(f"{inv_num} has no payment via bank_1 (Business Cheque)")

    # NZD overdue <= $10k should remain overdue (not paid)
    nzd_low_overdue = ["INV-0068", "INV-0087", "INV-0107", "INV-0039", "INV-0089",
                       "INV-0079", "INV-0104"]
    for inv_num in nzd_low_overdue:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            continue
        if inv.get("status") == "paid":
            errors.append(f"{inv_num} (NZD <= $10k) should NOT have been paid")

    if errors:
        return False, "; ".join(errors)
    return True, "AUD overdue paid via AUD Holding, NZD > $10k overdue paid via Business Cheque"
