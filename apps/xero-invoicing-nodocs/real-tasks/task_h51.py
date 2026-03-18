import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Update notes on every overdue invoice with total > $10,000."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    errors = []
    expected_note = "URGENT: High-value overdue - escalate to management"

    # Known overdue invoices with total > $10,000:
    # INV-0015 ($35,937.50), INV-0040 ($121,725), INV-0059 ($80,707),
    # INV-0063 ($14,921.25), INV-0100 ($13,785), INV-0102 ($60,975.88)
    expected_nums = ["INV-0015", "INV-0040", "INV-0059", "INV-0063", "INV-0100", "INV-0102"]

    for inv_num in expected_nums:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            errors.append(f"{inv_num} not found")
            continue
        notes = (inv.get("notes") or "").strip()
        if notes != expected_note:
            errors.append(f"{inv_num} notes is '{notes}', expected '{expected_note}'")

    # Overdue invoices with total <= $10,000 should NOT have the note
    low_value_overdue = ["INV-0068", "INV-0087", "INV-0107", "INV-0039", "INV-0089",
                         "INV-0079", "INV-0104", "INV-0033"]
    for inv_num in low_value_overdue:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            continue
        notes = (inv.get("notes") or "").strip()
        if notes == expected_note:
            errors.append(f"{inv_num} (total <= $10k) should NOT have the escalation note")

    if errors:
        return False, "; ".join(errors)
    return True, f"Notes updated on all {len(expected_nums)} high-value overdue invoices"
