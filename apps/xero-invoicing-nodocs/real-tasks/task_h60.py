import requests


def verify(server_url: str) -> tuple[bool, str]:
    """For awaiting approval invoices: approve and send those > $5,000,
    just approve those <= $5,000."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    errors = []

    # No awaiting_approval invoices should remain
    still_aa = [inv for inv in invoices if inv.get("status") == "awaiting_approval"]
    if still_aa:
        nums = [inv.get("invoiceNumber") for inv in still_aa]
        errors.append(f"Awaiting approval invoices still exist: {nums}")

    # > $5,000: approve AND send (sentAt must be set)
    # INV-0008 ($16,376), INV-0017 ($11,297.75), INV-0032 ($9,375),
    # INV-0045 ($9,918.75), INV-0066 ($60,500), INV-0077 ($5,478.50),
    # INV-0111 ($9,890), INV-0112 ($31,326)
    sent_nums = ["INV-0008", "INV-0017", "INV-0032", "INV-0045",
                 "INV-0066", "INV-0077", "INV-0111", "INV-0112"]
    for inv_num in sent_nums:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            errors.append(f"{inv_num} not found")
            continue
        if inv.get("status") != "awaiting_payment":
            errors.append(f"{inv_num} status is '{inv.get('status')}', expected 'awaiting_payment'")
        if not inv.get("sentAt"):
            errors.append(f"{inv_num} (> $5k) has no sentAt — should have been sent")

    # <= $5,000: approve only (sentAt should NOT be set)
    # INV-0038 ($2,875), INV-0056 ($655.50)
    approve_only_nums = ["INV-0038", "INV-0056"]
    for inv_num in approve_only_nums:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            errors.append(f"{inv_num} not found")
            continue
        if inv.get("status") != "awaiting_payment":
            errors.append(f"{inv_num} status is '{inv.get('status')}', expected 'awaiting_payment'")
        if inv.get("sentAt"):
            errors.append(f"{inv_num} (<= $5k) has sentAt set — should NOT have been sent")

    if errors:
        return False, "; ".join(errors)
    return True, "All AA invoices approved; > $5k also sent, <= $5k approved only"
