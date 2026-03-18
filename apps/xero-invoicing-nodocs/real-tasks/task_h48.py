import requests


def verify(server_url: str) -> tuple[bool, str]:
    """For all overdue invoices: void those with total < $5,000, pay those
    with total >= $5,000 via Business Cheque Account."""
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

    # No overdue invoices should remain
    still_overdue = [inv for inv in invoices if inv.get("status") == "overdue"]
    if still_overdue:
        nums = [inv.get("invoiceNumber") for inv in still_overdue]
        errors.append(f"Overdue invoices still exist: {nums}")

    # Known voided (total < $5,000): INV-0068, INV-0087, INV-0107, INV-0039
    for inv_num in ["INV-0068", "INV-0087", "INV-0107", "INV-0039"]:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            errors.append(f"{inv_num} not found")
        elif inv.get("status") != "voided":
            errors.append(f"{inv_num} status is '{inv.get('status')}', expected 'voided' (total < $5,000)")

    # Known paid (total >= $5,000): INV-0089, INV-0079, INV-0104, INV-0033,
    # INV-0100, INV-0063, INV-0015, INV-0102, INV-0059, INV-0040
    paid_nums = ["INV-0089", "INV-0079", "INV-0104", "INV-0033",
                 "INV-0100", "INV-0063", "INV-0015", "INV-0102", "INV-0059", "INV-0040"]
    for inv_num in paid_nums:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            errors.append(f"{inv_num} not found")
            continue
        if inv.get("status") != "paid":
            errors.append(f"{inv_num} status is '{inv.get('status')}', expected 'paid' (total >= $5,000)")
        if (inv.get("amountDue") or 0) > 0.01:
            errors.append(f"{inv_num} amountDue is {inv.get('amountDue')}, expected <= 0.01")
        inv_payments = [p for p in payments if p.get("invoiceId") == inv.get("id")]
        bank_ids = [p.get("bankAccountId") for p in inv_payments]
        if "bank_1" not in bank_ids:
            errors.append(f"{inv_num} has no payment via bank_1")

    if errors:
        return False, "; ".join(errors)
    return True, "All overdue invoices processed: < $5k voided, >= $5k paid via Business Cheque"
