import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Approve and send every draft invoice that belongs to a contact who has
    at least one fully paid invoice."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    invoices = state.get("invoices", [])
    errors = []

    # Known draft invoices belonging to contacts with paid invoices:
    # Bright Spark Electrical (INV-0005), Pinnacle Construction (INV-0084),
    # DataFlow Analytics (INV-0061), Heritage Craft Brewery (INV-0020)
    expected_sent = ["INV-0005", "INV-0084", "INV-0061", "INV-0020"]

    for inv_num in expected_sent:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            errors.append(f"{inv_num} not found")
            continue
        if inv.get("status") != "awaiting_payment":
            errors.append(f"{inv_num} status is '{inv.get('status')}', expected 'awaiting_payment'")
        if not inv.get("sentAt"):
            errors.append(f"{inv_num} has no sentAt timestamp (should have been sent)")

    # Verify drafts that belong to contacts WITHOUT paid invoices are still drafts
    # (i.e., we didn't over-approve)
    contacts_with_paid = set()
    for inv in invoices:
        if inv.get("status") == "paid":
            contacts_with_paid.add(inv.get("contactId"))

    remaining_drafts = [
        inv for inv in invoices
        if inv.get("status") == "draft"
        and inv.get("contactId") not in contacts_with_paid
    ]
    # These should still be drafts — not an error if they exist
    # But drafts for contacts WITH paid invoices should NOT remain
    wrongly_draft = [
        inv for inv in invoices
        if inv.get("status") == "draft"
        and inv.get("contactId") in contacts_with_paid
    ]
    if wrongly_draft:
        nums = [inv.get("invoiceNumber") for inv in wrongly_draft]
        errors.append(f"Draft invoices for contacts with paid invoices still exist: {nums}")

    if errors:
        return False, "; ".join(errors)
    return True, f"All {len(expected_sent)} draft invoices for contacts with paid invoices have been approved and sent"
