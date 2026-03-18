import requests


def verify(server_url: str) -> tuple[bool, str]:
    """Delete all draft invoices for contacts outside New Zealand.
    Approve all remaining draft invoices."""
    try:
        resp = requests.get(f"{server_url}/api/state")
        if resp.status_code != 200:
            return False, f"Failed to fetch state: HTTP {resp.status_code}"
        state = resp.json()
    except Exception as e:
        return False, f"Error fetching state: {e}"

    contacts = state.get("contacts", [])
    invoices = state.get("invoices", [])
    errors = []

    # Non-NZ contact IDs
    non_nz_ids = set()
    for c in contacts:
        addr = c.get("billingAddress", {})
        if addr.get("country") != "New Zealand":
            non_nz_ids.add(c.get("id"))

    # Verify INV-0061 (DataFlow, US) is deleted
    inv_0061 = next((i for i in invoices if i.get("invoiceNumber") == "INV-0061"), None)
    if inv_0061 is not None:
        errors.append("INV-0061 (non-NZ draft) should have been deleted but still exists")

    # No draft invoices should remain for non-NZ contacts
    non_nz_drafts = [
        inv for inv in invoices
        if inv.get("contactId") in non_nz_ids and inv.get("status") == "draft"
    ]
    if non_nz_drafts:
        nums = [inv.get("invoiceNumber") for inv in non_nz_drafts]
        errors.append(f"Non-NZ draft invoices still exist: {nums}")

    # No draft invoices should remain for NZ contacts (all should be approved)
    nz_ids = set(c.get("id") for c in contacts) - non_nz_ids
    nz_drafts = [
        inv for inv in invoices
        if inv.get("contactId") in nz_ids and inv.get("status") == "draft"
    ]
    if nz_drafts:
        nums = [inv.get("invoiceNumber") for inv in nz_drafts]
        errors.append(f"NZ draft invoices still not approved: {nums}")

    # Verify known NZ drafts are now awaiting_payment
    known_nz_drafts = [
        "INV-0005", "INV-0018", "INV-0020", "INV-0025", "INV-0042",
        "INV-0054", "INV-0082", "INV-0083", "INV-0084", "INV-0093", "INV-0108",
    ]
    for inv_num in known_nz_drafts:
        inv = next((i for i in invoices if i.get("invoiceNumber") == inv_num), None)
        if inv is None:
            errors.append(f"{inv_num} not found")
        elif inv.get("status") != "awaiting_payment":
            errors.append(f"{inv_num} status is '{inv.get('status')}', expected 'awaiting_payment'")

    if errors:
        return False, "; ".join(errors)
    return True, "Non-NZ draft invoices deleted, all NZ draft invoices approved"
